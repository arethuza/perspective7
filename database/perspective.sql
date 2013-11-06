﻿drop table if exists item_binary_data cascade;

create table item_binary_data
(
    id                  serial      primary key not null,
    data                bytea       not null
);

drop table if exists items cascade;

create table items 
(
    id                  serial      primary key not null,
    parent_id           int         references items(id),
    name                text        not null,
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
    search_vector       tsvector,
    binary_data_id      int         references item_binary_data(id)
); 

alter sequence items_id_seq minvalue 0 start 0;

drop table if exists item_versions cascade;

create table item_versions 
(
    item_id             int         references items(id),
    version             int         not null,
    type_id             int         references items(id),
    json_data           json        not null,
    saved_at            timestamp   not null,
    saved_by            int         references items(id)
);

create or replace function items_index_search_text() returns trigger as $$
begin   
    new.search_vector = to_tsvector('pg_catalog.english', new.search_text);
    new.search_text = null;
    return new;
end;
$$ language plpgsql;

create trigger item_index_trigger before insert or update
on items for each row execute procedure items_index_search_text();
