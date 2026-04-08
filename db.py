from datetime import datetime
from uuid import UUID

from idli import AutoUUID, BTreeIndex, Connection, HNSWIndex, Vector
import jwt

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
    loc_locality: str | None
    loc_region: str | None
    loc_country: str | None
    loc_postcode: str | None
    employment_type: str | None
    date_posted: datetime
    valid_through: datetime | None
    description: str

    match_vec: Vector(768) | None
    
    __idli__ = [
        BTreeIndex('url'),
        BTreeIndex('-date_posted'),
        HNSWIndex('match_vec', 'cos'),
    ]


    @classmethod
    def add(cls, url: str, src: str, details: dict):
        exists = cls.select(url=url).one()
        if exists:
            return

        job = Job(url=url, src=src, indexed_at=datetime.now())

        for key in [
            'title', 'org_name', 'org_logo', 'is_remote',
            'loc_locality', 'loc_region', 'loc_country', 'loc_postcode',
            'employment_type', 'date_posted', 'valid_through', 'description',
            'match_vec',
        ]:
            setattr(job, key, details[key])
        
        job.save()
    
    @property
    def fmt_time_ago(self):
        return to_time_ago(self.date_posted)


@db.Model
class ClientUser:
    id: UUID = AutoUUID
    name: str
    email: str
    client: str
    
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


@db.Model
class UserResume:
    id: UUID
    filename: str
    match_vec: Vector(768)
    updated: datetime
    
    @property
    def updated_time_ago(self):
        return to_time_ago(self.updated)