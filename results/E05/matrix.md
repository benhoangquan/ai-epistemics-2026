Detection rate (all 40 instances; coop/local split in matrix.csv)

| attack (timing) | n | G0 | G1 | G2 | G3 | G4 |
|---|---|---|---|---|---|---|
| edit_naive (post_hoc) | 40 | 0.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| edit_rehash (post_hoc) | 40 | 0.00 | 0.00 | 1.00 | 1.00 | 1.00 |
| delete_naive (post_hoc) | 40 | 0.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| delete_rehash (post_hoc) | 40 | 0.00 | 0.00 | 1.00 | 1.00 | 1.00 |
| truncate (post_hoc) | 40 | 0.00 | 0.00 | 1.00 | 1.00 | 1.00 |
| reorder_naive (post_hoc) | 40 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| reorder_rehash (post_hoc) | 40 | 0.00 | 0.00 | 1.00 | 1.00 | 1.00 |
| insert_post (post_hoc) | 40 | 0.00 | 0.00 | 1.00 | 1.00 | 1.00 |
| rewrite_resign (post_hoc) | 40 | 0.00 | 0.00 | 1.00 | 1.00 | 1.00 |
| fork (post_hoc) | 40 | 0.00 | 0.00 | 1.00 | 1.00 | 1.00 |
| fabricate_post (post_hoc) | 40 | 0.00 | 0.00 | 1.00 | 1.00 | 1.00 |
| window_delete (live) | 20 | 0.00 | 0.00 | 0.00 | 0.15 | 1.00 |
| window_relabel (live) | 20 | 0.00 | 0.00 | 0.00 | 0.50 | 0.50 |
| source_omit (at_source) | 40 | 0.00 | 0.00 | 0.00 | 0.10 | 1.00 |
| source_relabel (at_source) | 40 | 0.00 | 0.00 | 0.00 | 0.50 | 0.50 |
| source_relabel_len (at_source) | 40 | 0.00 | 0.00 | 0.00 | 0.50 | 1.00 |
| source_fabricate (at_source) | 40 | 0.00 | 0.00 | 0.00 | 0.50 | 0.50 |
| source_insert (at_source) | 40 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 |
