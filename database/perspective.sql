drop table if exists items cascade;

create table items 
(
    id                  serial      primary key not null,
    parent_id           int         references items(id) on delete cascade,
    name                text        not null,
    deletable		boolean	    not null default true,
    version             int         not null default 0,
    id_path             ltree,
    type_id             int         references items(id),
    type_path           ltree,
    json_data           json        not null,
    created_at          timestamp   not null,
    created_by          int         references items(id),
    saved_at            timestamp   not null,
    saved_by            int         references items(id),
    search_text         text,
    search_vector       tsvector
);

alter sequence items_id_seq minvalue 0 start 0;

create unique index parent_id_name_idx on items (parent_id, name);

drop table if exists item_versions cascade;

create table item_versions 
(
    item_id             int         references items(id) on delete cascade,
    version             int         not null,
    type_id             int         references items(id),
    json_data           json        not null,
    saved_at            timestamp   not null,
    saved_by            int         references items(id)
);

create or replace function items_index_search_text() returns trigger as $$
begin
    if new.search_text is not null then
        new.search_vector = to_tsvector('pg_catalog.english', new.search_text);
        new.search_text = null;
    end if;
    return new;
end;
$$ language plpgsql;

create trigger item_index_trigger before insert or update
on items for each row execute procedure items_index_search_text();

drop table if exists tokens cascade;

create table tokens
(
    item_id             int         references items(id) on delete cascade,
    token_value         text        not null,
    json_data           json        not null,
    created_at          timestamp   not null,
    expires_at          timestamp   not null
);

drop table if exists file_versions cascade;

create table file_versions
(
    item_id             int         references items(id) on delete cascade,
    file_version        int         not null default 0,
    previous_version	int,
    length              int         not null default 0,
    hash                text,
    created_at          timestamp   not null,
    created_by          int         references items(id),
    
    constraint no_duplicate_file_version unique (item_id, file_version)
);

drop table if exists file_blocks cascade;

create table file_blocks 
(
    item_id                 int         references items(id) on delete cascade,
    file_version            int         not null,
    block_number            int         not null,
    data_file_version       int         null,
    length	                int         not null,
    hash                    text        null,
    created_at              timestamp   not null,
    data                    bytea       null,
    
    constraint no_duplicate_file_block unique (item_id, file_version, block_number)
);

