from datetime import datetime
from uuid import UUID

from idli import AutoUUID, BTreeIndex, Connection, HNSWIndex, Vector

import config

db = Connection(config.DB_URI, sambar_dip=True)


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


if __name__ == '__main__':
    board = Board(url='https://jobs.lever.co/welocalize')
    board.save()
