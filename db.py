from datetime import datetime
import json
from uuid import UUID

from idli import AutoUUID, BTreeIndex, Connection, HNSWIndex, PrimaryKey, Vector, VNN
import jwt
import mistune
import nh3
import niquests

import config

db = Connection(config.DB_URI, sambar_dip=True, extensions=['pgvector'])


def to_time_ago(dt: datetime | None):
    if not dt:
        return ''
        
    diff = datetime.now() - dt
    seconds = int(diff.total_seconds())

    if seconds < 60:
        return f"{seconds} seconds ago"
    
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes} minutes ago"
    
    hours = minutes // 60
    if hours < 24:
        return f"{hours} hours ago"
    
    days = hours // 24
    return f"{days} days ago"
      

@db.Model
class Board:
    id: UUID = AutoUUID
    url: str
    src: str
    last_crawled: datetime = datetime(1970, 1, 1)
    redirect_url: str | None = None

    __idli__ = [
        BTreeIndex('url'),
        BTreeIndex('src', 'last_crawled'),
    ]


    @classmethod
    def add(cls, url, src):
        exists = cls.select(url=url).one()
        if not exists:
            cls(url=url, src=src).save()


@db.Model
class JobUrl:
    id: UUID = AutoUUID
    url: str
    src: str
    discovered_at: datetime = datetime.now()
    crawled_at: datetime | None
    crawl_error: str | None

    __idli__ = [
        BTreeIndex('url'),
        BTreeIndex('crawled_at', 'discovered_at')
    ]


    @classmethod
    def add(cls, url, src):
        exists = cls.select(url=url).one()
        if not exists:
            cls(url=url, src=src).save()


@db.Model
class Job:
    id: UUID = AutoUUID
    url: str
    src: str

    indexed_at: datetime

    title: str
    org_name: str
    org_logo: str | None
    is_remote: bool
    loc_json: str | None
    loc_locality: str | None
    loc_region: str | None
    loc_country: str | None
    loc_postcode: str | None
    employment_type: str | None
    date_posted: datetime
    valid_through: datetime | None
    description: str

    match_vec: Vector(768) | None
    pplx_vec: Vector(1024) | None
    
    __idli__ = [
        BTreeIndex('url'),
        BTreeIndex('-date_posted'),
        HNSWIndex('match_vec', 'cos'),
        HNSWIndex('pplx_vec', 'cos'),
    ]


    @classmethod
    def add(cls, url: str, src: str, details: dict):
        exists = cls.select(url=url).one()
        if exists:
            return

        job = Job(url=url, src=src, indexed_at=datetime.now())

        for key in [
            'title', 'org_name', 'org_logo', 'is_remote',
            'loc_json',
            'employment_type', 'date_posted', 'valid_through', 'description',
            'pplx_vec',
        ]:
            setattr(job, key, details[key])
        
        job.save()
    
    
    @property
    def fmt_time_ago(self):
        return to_time_ago(self.date_posted)
    
    
    @property
    def loc_str(self):
        if not self.loc_json:
            return 'Unknown'
        loc = json.loads(self.loc_json)
        if type(loc) is dict:
            loc = [loc]
        
        places = []
        for obj in loc:
            addr = obj['address']
            names = [
                addr.get('addressLocality'),
                addr.get('addressRegion'),
                addr.get('addressCountry'),
            ]
            places.append(', '.join([n for n in names if n]))
            
        places = [p for p in places if p]
        if not places:
            return "Unknown"
        return " / ".join(places)
    
    
    def is_still_live(self):
        r = niquests.head(self.url)
        return r.status_code == 200
    
    
    def get_similar_jobs(self, count=10):
        vec = self.pplx_vec.tolist()
        jobs = list(Job.select().only(
            'id', 'title', 'org_logo', 'org_name',
            'loc_json', 'date_posted', 'pplx_vec',
        ).order_by(VNN.cos('pplx_vec', vec))[1:count+1])
        return jobs
    
    
    def archive(self):
        
        a_job = ArchivedJob(
            id = self.id,
            url = self.url,
            src = self.src,
            
            indexed_at = self.indexed_at,
            archived_at = datetime.now(),
            
            title = self.title,
            org_name = self.org_name,
            org_logo = self.org_logo,
            is_remote = self.is_remote,
            loc_json = self.loc_json,
            
            employment_type = self.employment_type,
            date_posted = self.date_posted,
            valid_through = self.valid_through,
            description = self.description,
            
            pplx_vec = self.pplx_vec,
        )
        
        a_job.save()
        self.delete()
        
        
@db.Model
class ArchivedJob:
    id: UUID
    url: str
    src: str

    indexed_at: datetime
    archived_at: datetime

    title: str
    org_name: str
    org_logo: str | None
    is_remote: bool
    loc_json: str | None
    employment_type: str | None
    date_posted: datetime
    valid_through: datetime | None
    description: str

    pplx_vec: Vector(1024) | None


@db.Model
class JobLoc:
    job_id: UUID
    loc_tag: str
    
    __idli__ = [
        PrimaryKey('loc_tag', 'job_id')
    ]
    
    @classmethod
    def add_tag(cls, job_id, loc_tag):
        existing = cls.select(job_id=job_id, loc_tag=loc_tag).one()
        if not existing:
            new_obj = cls(job_id=job_id, loc_tag=loc_tag)
            new_obj.save()
    
    
    
@db.Model
class ClientUser:
    id: UUID = AutoUUID
    name: str
    email: str
    client: str
    credits: int = 0
    credits_last_used: datetime = datetime(1970, 1, 1)
    
    # match_vec: Vector(768) | None
    # add separate table
    
    __idli__ = [
        BTreeIndex('email', 'client')
    ]
    
    
    @classmethod
    def add(cls, name: str, email: str, client: str):
        exists = cls.select(email=email, client=client).one()
        if exists:
            return False
        
        user = cls(name=name, email=email, client=client)
        user.save()
        return True
    
        
    @classmethod
    def get_by_email(cls, email: str, client: str):
        return cls.select(email=email, client=client).one()


    @classmethod
    def get_by_jwt(cls, encoded_jwt: str | None, iss: str):
        if not encoded_jwt:
            return None
        try:
            decoded_contents = jwt.decode(
                encoded_jwt, config.JWT_SECRET, algorithms=["HS256"]
            )
            assert decoded_contents['iss'] == iss
            email = decoded_contents['email']
            return cls.select(email=email, client=iss).one()
        except:
            return None

    
    def generate_jwt(self):
        encoded_jwt = jwt.encode(
            {'iss': self.client, 'email': self.email},
            config.JWT_SECRET,
            algorithm = 'HS256',
        )
        return encoded_jwt
    
    
    def debit(self, credits: int, note: str, api_usage: dict):
        timestamp = datetime.now()
        
        usage_log = CreditUseLog(
            user_id = self.id,
            timestamp = timestamp,
            credits = credits,
            note = note,
            api_usage = json.dumps(api_usage)
        )
        usage_log.save()
      
        self.credits = self.credits - credits
        self.credits_last_used = timestamp
        self.save()
    
        
    @property
    def credits_last_used_time_ago(self):
        return to_time_ago(self.credits_last_used)


@db.Model
class UserResume:
    id: UUID
    filename: str
    markdown_content: str = ''
    match_vec: Vector(768) | None
    pplx_vec: Vector(1024)
    updated: datetime
    
    @property
    def updated_time_ago(self):
        return to_time_ago(self.updated)


@db.Model    
class UserJob:
    id: UUID = AutoUUID
    user_id: UUID
    job_id: UUID
    
    starred_at: datetime | None
    
    applied_at: datetime | None
    
    # custom resume
    cr_markdown_content: str | None
    cr_generated_at: datetime | None
    
    __idli__ = [
        BTreeIndex('user_id', 'job_id')
    ]
    
    @property
    def cr_html_content(self):
        unsafe_html = mistune.html(self.cr_markdown_content)
        safe_html = nh3.clean(unsafe_html)
        return safe_html
    
    
    @classmethod
    def get_for_pair(cls, user_id: str, job_id: str):
        existing = cls.select(user_id = user_id, job_id = job_id).one()
        if existing:
            return existing
        else:
            return cls(user_id = user_id, job_id = job_id)


# Deprecated
@db.Model
class CustomizedResume:
    id: UUID = AutoUUID
    user_id: UUID
    job_id: UUID
    markdown_content: str
    created: datetime
    updated: datetime
    pdf_timestamp: datetime = datetime(1970, 1, 1)
    
    __idli__ = [
        BTreeIndex('user_id', 'job_id')
    ]
    
    @property
    def html_content(self):
        unsafe_html = mistune.html(self.markdown_content)
        safe_html = nh3.clean(unsafe_html)
        return safe_html

        
@db.Model
class CreditUseLog:
    id: UUID = AutoUUID
    user_id: UUID
    timestamp: datetime
    credits: int
    note: str
    api_usage: str
    
    __idli__ = [
        BTreeIndex('user_id', '-timestamp')
    ]
    
    @property
    def time_ago(self):
        return to_time_ago(self.timestamp)
        
    
    @property
    def note_simple(self):
        note_type = self.note.split(':')[0]
        if note_type == 'CUSTOMIZE_RESUME':
            return 'Resume Customization'
        
        return note_type