# create range distributed table to test behavior of SELECT in concurrent operations
setup
{
	SET citus.shard_replication_factor TO 1;
    CREATE TABLE select_hash(id integer, data text);
	SELECT create_distributed_table('select_hash', 'id');
	COPY select_hash FROM PROGRAM 'echo 0, a\\n1, b\\n2, c\\n3, d\\n4, e' WITH CSV;
}

# drop distributed table
teardown
{
    DROP TABLE IF EXISTS select_hash CASCADE;
}

# session 1
session "s1"
step "s1-begin" { BEGIN; }
step "s1-select" { SELECT * FROM select_hash ORDER BY id, data; }
step "s1-insert" { INSERT INTO select_hash VALUES(0, 'k'); }
step "s1-update" { UPDATE select_hash SET data = 'l' WHERE id = 0; }
step "s1-upsert" { INSERT INTO select_hash VALUES(0, 'm') ON CONFLICT ON CONSTRAINT select_hash_unique DO UPDATE SET data = 'l'; }
step "s1-delete" { DELETE FROM select_hash WHERE id = 1; }
step "s1-truncate" { TRUNCATE select_hash; }
step "s1-drop" { DROP TABLE select_hash; }
step "s1-ddl-create-index" { CREATE INDEX select_hash_index ON select_hash(id); }
step "s1-ddl-drop-index" { DROP INDEX select_hash_index; }
step "s1-ddl-add-column" { ALTER TABLE select_hash ADD new_column int DEFAULT 0; }
step "s1-ddl-drop-column" { ALTER TABLE select_hash DROP new_column; }
step "s1-ddl-rename-column" { ALTER TABLE select_hash RENAME data TO new_data; }
step "s1-ddl-unique-constraint" { ALTER TABLE select_hash ADD CONSTRAINT select_hash_unique UNIQUE(id); }
step "s1-table-size" { SELECT citus_table_size('select_hash'); SELECT citus_relation_size('select_hash'); SELECT citus_total_relation_size('select_hash'); }
step "s1-master-modify-multiple-shards" { SELECT master_modify_multiple_shards('DELETE FROM select_hash;'); }
step "s1-create-non-distributed-table" { CREATE TABLE select_hash(id integer, data text); COPY select_hash FROM PROGRAM 'echo 0, a\\n1, b\\n2, c\\n3, d\\n4, e' WITH CSV; }
step "s1-distribute-table" { SELECT create_distributed_table('select_hash', 'id'); }
step "s1-commit" { COMMIT; }

# session 2
session "s2"
step "s2-begin" { BEGIN; }
step "s2-select" { SELECT * FROM select_hash ORDER BY id, data; }
step "s2-insert" { INSERT INTO select_hash VALUES(0, 'k'); }
step "s2-update" { UPDATE select_hash SET data = 'l' WHERE id = 0; }
step "s2-upsert" { INSERT INTO select_hash VALUES(0, 'm') ON CONFLICT ON CONSTRAINT select_hash_unique DO UPDATE SET data = 'l'; }
step "s2-delete" { DELETE FROM select_hash WHERE id = 1; }
step "s2-truncate" { TRUNCATE select_hash; }
step "s2-drop" { DROP TABLE select_hash; }
step "s2-ddl-create-index" { CREATE INDEX select_hash_index ON select_hash(id); }
step "s2-ddl-drop-index" { DROP INDEX select_hash_index; }
step "s2-ddl-add-column" { ALTER TABLE select_hash ADD new_column int DEFAULT 0; }
step "s2-ddl-drop-column" { ALTER TABLE select_hash DROP new_column; }
step "s2-ddl-rename-column" { ALTER TABLE select_hash RENAME data TO new_data; }
step "s2-ddl-unique-constraint" { ALTER TABLE select_hash ADD CONSTRAINT select_hash_unique UNIQUE(id); }
step "s2-table-size" { SELECT citus_table_size('select_hash'); SELECT citus_relation_size('select_hash'); SELECT citus_total_relation_size('select_hash'); }
step "s2-master-modify-multiple-shards" { SELECT master_modify_multiple_shards('DELETE FROM select_hash;'); }
step "s2-create-non-distributed-table" { CREATE TABLE select_hash(id integer, data text); COPY select_hash FROM PROGRAM 'echo 0, a\\n1, b\\n2, c\\n3, d\\n4, e' WITH CSV; }
step "s2-distribute-table" { SELECT create_distributed_table('select_hash', 'id'); }
step "s2-commit" { COMMIT; }

# permutations - SELECT vs SELECT
permutation "s1-begin" "s2-begin" "s1-select" "s2-select" "s1-commit" "s2-commit" "s1-select"

# permutations - SELECT first
permutation "s1-begin" "s2-begin" "s1-select" "s2-insert" "s1-commit" "s2-commit" "s1-select"
permutation "s1-begin" "s2-begin" "s1-select" "s2-update" "s1-commit" "s2-commit" "s1-select"
permutation "s1-ddl-unique-constraint" "s1-begin" "s2-begin" "s1-select" "s2-upsert" "s1-commit" "s2-commit" "s1-select"
permutation "s1-begin" "s2-begin" "s1-select" "s2-delete" "s1-commit" "s2-commit" "s1-select"
permutation "s1-begin" "s2-begin" "s1-select" "s2-truncate" "s1-commit" "s2-commit" "s1-select"
permutation "s1-begin" "s2-begin" "s1-select" "s2-drop" "s1-commit" "s2-commit" "s1-select"
permutation "s1-begin" "s2-begin" "s1-select" "s2-ddl-create-index" "s1-commit" "s2-commit" "s1-select"
permutation "s1-ddl-create-index" "s1-begin" "s2-begin" "s1-select" "s2-ddl-drop-index" "s1-commit" "s2-commit" "s1-select"
permutation "s1-begin" "s2-begin" "s1-select" "s2-ddl-add-column" "s1-commit" "s2-commit" "s1-select"
permutation "s1-ddl-add-column" "s1-begin" "s2-begin" "s1-select" "s2-ddl-drop-column" "s1-commit" "s2-commit" "s1-select"
permutation "s1-begin" "s2-begin" "s1-select" "s2-ddl-unique-constraint" "s1-commit" "s2-commit" "s1-select"
permutation "s1-begin" "s2-begin" "s1-select" "s2-table-size" "s1-commit" "s2-commit" "s1-select"
permutation "s1-begin" "s2-begin" "s1-select" "s2-master-modify-multiple-shards" "s1-commit" "s2-commit" "s1-select"
permutation "s1-drop" "s1-create-non-distributed-table" "s1-begin" "s2-begin" "s1-select" "s2-distribute-table" "s1-commit" "s2-commit" "s1-select"

# permutations - SELECT second
permutation "s1-begin" "s2-begin" "s1-insert" "s2-select" "s1-commit" "s2-commit" "s1-select"
permutation "s1-begin" "s2-begin" "s1-update" "s2-select" "s1-commit" "s2-commit" "s1-select"
permutation "s1-ddl-unique-constraint" "s1-begin" "s2-begin" "s1-upsert" "s2-select" "s1-commit" "s2-commit" "s1-select"
permutation "s1-begin" "s2-begin" "s1-delete" "s2-select" "s1-commit" "s2-commit" "s1-select"
permutation "s1-begin" "s2-begin" "s1-truncate" "s2-select" "s1-commit" "s2-commit" "s1-select"
permutation "s1-begin" "s2-begin" "s1-drop" "s2-select" "s1-commit" "s2-commit" "s1-select"
permutation "s1-begin" "s2-begin" "s1-ddl-create-index" "s2-select" "s1-commit" "s2-commit" "s1-select"
permutation "s1-ddl-create-index" "s1-begin" "s2-begin" "s1-ddl-drop-index" "s2-select" "s1-commit" "s2-commit" "s1-select"
permutation "s1-begin" "s2-begin" "s1-ddl-add-column" "s2-select" "s1-commit" "s2-commit" "s1-select"
permutation "s1-ddl-add-column" "s1-begin" "s2-begin" "s1-ddl-drop-column" "s2-select" "s1-commit" "s2-commit" "s1-select"
permutation "s1-begin" "s2-begin" "s1-ddl-unique-constraint" "s2-select" "s1-commit" "s2-commit" "s1-select"
permutation "s1-begin" "s2-begin" "s1-table-size" "s2-select" "s1-commit" "s2-commit" "s1-select"
permutation "s1-begin" "s2-begin" "s1-master-modify-multiple-shards" "s2-select" "s1-commit" "s2-commit" "s1-select"
permutation "s1-drop" "s1-create-non-distributed-table" "s1-begin" "s2-begin" "s1-distribute-table" "s2-select" "s1-commit" "s2-commit" "s1-select"


