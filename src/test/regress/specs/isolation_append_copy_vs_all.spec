# create append distributed table to test behavior of COPY in concurrent operations
setup
{
	SET citus.shard_replication_factor TO 1;
    CREATE TABLE append_copy(id integer, data text);
	SELECT create_distributed_table('append_copy', 'id', 'append');
	COPY append_copy FROM PROGRAM 'echo 0, a\\n1, b\\n2, c\\n3, d\\n4, e' WITH CSV;
}

# drop distributed table
teardown
{
    DROP TABLE IF EXISTS append_copy CASCADE;
}

# session 1
session "s1"
step "s1-begin" { BEGIN; }
step "s1-copy" { COPY append_copy FROM PROGRAM 'echo 5, f\\n6, g\\n7, h\\n8, i\\n9, j' WITH CSV; }
step "s1-copy-additional-column" { COPY append_copy FROM PROGRAM 'echo 5, f, 5\\n6, g, 6\\n7, h, 7\\n8, i, 8\\n9, j, 9' WITH CSV; }
step "s1-copy-duplicate" { COPY append_copy FROM PROGRAM 'echo 0, f\\n1, g\\n2, h\\n3, i\\n4, j' WITH CSV; }
step "s1-select" { SELECT * FROM append_copy ORDER BY id, data; }
step "s1-update" { UPDATE append_copy SET data = 'l' WHERE id = 0; }
step "s1-delete" { DELETE FROM append_copy WHERE id = 1; }
step "s1-truncate" { TRUNCATE append_copy; }
step "s1-drop" { DROP TABLE append_copy; }
step "s1-ddl-create-index" { CREATE INDEX append_copy_index ON append_copy(id); }
step "s1-ddl-drop-index" { DROP INDEX append_copy_index; }
step "s1-ddl-add-column" { ALTER TABLE append_copy ADD new_column int DEFAULT 0; }
step "s1-ddl-drop-column" { ALTER TABLE append_copy DROP new_column; }
step "s1-ddl-rename-column" { ALTER TABLE append_copy RENAME data TO new_data; }
step "s1-ddl-unique-constraint" { ALTER TABLE append_copy ADD CONSTRAINT append_copy_unique UNIQUE(id); }
step "s1-table-size" { SELECT citus_table_size('append_copy'); SELECT citus_relation_size('append_copy'); SELECT citus_total_relation_size('append_copy'); }
step "s1-master-modify-multiple-shards" { SELECT master_modify_multiple_shards('DELETE FROM append_copy;'); }
step "s1-create-non-distributed-table" { CREATE TABLE append_copy(id integer, data text); COPY append_copy FROM PROGRAM 'echo 0, a\\n1, b\\n2, c\\n3, d\\n4, e' WITH CSV; }
step "s1-distribute-table" { SELECT create_distributed_table('append_copy', 'id'); }
step "s1-commit" { COMMIT; }

# session 2
session "s2"
step "s2-begin" { BEGIN; }
step "s2-copy" { COPY append_copy FROM PROGRAM 'echo 5, f\\n6, g\\n7, h\\n8, i\\n9, j' WITH CSV; }
step "s2-copy-additional-column" { COPY append_copy FROM PROGRAM 'echo 5, f, 5\\n6, g, 6\\n7, h, 7\\n8, i, 8\\n9, j, 9' WITH CSV; }
step "s2-copy-duplicate" { COPY append_copy FROM PROGRAM 'echo 0, f\\n1, g\\n2, h\\n3, i\\n4, j' WITH CSV; }
step "s2-select" { SELECT * FROM append_copy ORDER BY id, data; }
step "s2-update" { UPDATE append_copy SET data = 'l' WHERE id = 0; }
step "s2-delete" { DELETE FROM append_copy WHERE id = 1; }
step "s2-truncate" { TRUNCATE append_copy; }
step "s2-drop" { DROP TABLE append_copy; }
step "s2-ddl-create-index" { CREATE INDEX append_copy_index ON append_copy(id); }
step "s2-ddl-drop-index" { DROP INDEX append_copy_index; }
step "s2-ddl-add-column" { ALTER TABLE append_copy ADD new_column int DEFAULT 0; }
step "s2-ddl-drop-column" { ALTER TABLE append_copy DROP new_column; }
step "s2-ddl-rename-column" { ALTER TABLE append_copy RENAME data TO new_data; }
step "s2-ddl-unique-constraint" { ALTER TABLE append_copy ADD CONSTRAINT append_copy_unique UNIQUE(id); }
step "s2-table-size" { SELECT citus_table_size('append_copy'); SELECT citus_relation_size('append_copy'); SELECT citus_total_relation_size('append_copy'); }
step "s2-master-modify-multiple-shards" { SELECT master_modify_multiple_shards('DELETE FROM append_copy;'); }
step "s2-create-non-distributed-table" { CREATE TABLE append_copy(id integer, data text); COPY append_copy FROM PROGRAM 'echo 0, a\\n1, b\\n2, c\\n3, d\\n4, e' WITH CSV; }
step "s2-distribute-table" { SELECT create_distributed_table('append_copy', 'id'); }
step "s2-commit" { COMMIT; }

# permutations - COPY vs COPY
permutation "s1-begin" "s2-begin" "s1-copy" "s2-copy" "s1-commit" "s2-commit" "s1-select"

# permutations - COPY first
permutation "s1-begin" "s2-begin" "s1-copy" "s2-select" "s1-commit" "s2-commit" "s1-select"
permutation "s1-begin" "s2-begin" "s1-copy" "s2-update" "s1-commit" "s2-commit" "s1-select"
permutation "s1-begin" "s2-begin" "s1-copy" "s2-delete" "s1-commit" "s2-commit" "s1-select"
permutation "s1-begin" "s2-begin" "s1-copy" "s2-truncate" "s1-commit" "s2-commit" "s1-select"
permutation "s1-begin" "s2-begin" "s1-copy" "s2-drop" "s1-commit" "s2-commit" "s1-select"
permutation "s1-begin" "s2-begin" "s1-copy" "s2-ddl-create-index" "s1-commit" "s2-commit" "s1-select"
permutation "s1-ddl-create-index" "s1-begin" "s2-begin" "s1-copy" "s2-ddl-drop-index" "s1-commit" "s2-commit" "s1-select"
permutation "s1-begin" "s2-begin" "s1-copy" "s2-ddl-add-column" "s1-commit" "s2-commit" "s1-select"
permutation "s1-ddl-add-column" "s1-begin" "s2-begin" "s1-copy-additional-column" "s2-ddl-drop-column" "s1-commit" "s2-commit" "s1-select"
permutation "s1-begin" "s2-begin" "s1-copy" "s2-ddl-unique-constraint" "s1-commit" "s2-commit" "s1-select"
permutation "s1-begin" "s2-begin" "s1-copy-duplicate" "s2-ddl-unique-constraint" "s1-commit" "s2-commit" "s1-select"
permutation "s1-begin" "s2-begin" "s1-copy" "s2-table-size" "s1-commit" "s2-commit" "s1-select"
permutation "s1-begin" "s2-begin" "s1-copy" "s2-master-modify-multiple-shards" "s1-commit" "s2-commit" "s1-select"
permutation "s1-drop" "s1-create-non-distributed-table" "s1-begin" "s2-begin" "s1-copy" "s2-distribute-table" "s1-commit" "s2-commit" "s1-select"

# permutations - COPY second
permutation "s1-begin" "s2-begin" "s1-select" "s2-copy" "s1-commit" "s2-commit" "s1-select"
permutation "s1-begin" "s2-begin" "s1-update" "s2-copy" "s1-commit" "s2-commit" "s1-select"
permutation "s1-begin" "s2-begin" "s1-delete" "s2-copy" "s1-commit" "s2-commit" "s1-select"
permutation "s1-begin" "s2-begin" "s1-truncate" "s2-copy" "s1-commit" "s2-commit" "s1-select"
permutation "s1-begin" "s2-begin" "s1-drop" "s2-copy" "s1-commit" "s2-commit" "s1-select"
permutation "s1-begin" "s2-begin" "s1-ddl-create-index" "s2-copy" "s1-commit" "s2-commit" "s1-select"
permutation "s1-ddl-create-index" "s1-begin" "s2-begin" "s1-ddl-drop-index" "s2-copy" "s1-commit" "s2-commit" "s1-select"
permutation "s1-begin" "s2-begin" "s1-ddl-add-column" "s2-copy" "s1-commit" "s2-commit" "s1-select"
permutation "s1-ddl-add-column" "s1-begin" "s2-begin" "s1-ddl-drop-column" "s2-copy" "s1-commit" "s2-commit" "s1-select"
permutation "s1-begin" "s2-begin" "s1-ddl-unique-constraint" "s2-copy" "s1-commit" "s2-commit" "s1-select"
permutation "s1-begin" "s2-begin" "s1-ddl-unique-constraint" "s2-copy-duplicate" "s1-commit" "s2-commit" "s1-select"
permutation "s1-begin" "s2-begin" "s1-table-size" "s2-copy" "s1-commit" "s2-commit" "s1-select"
permutation "s1-begin" "s2-begin" "s1-master-modify-multiple-shards" "s2-copy" "s1-commit" "s2-commit" "s1-select"
permutation "s1-drop" "s1-create-non-distributed-table" "s1-begin" "s2-begin" "s1-distribute-table" "s2-copy" "s1-commit" "s2-commit" "s1-select"


