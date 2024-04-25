sql = '''SELECT t2.* FROM (
    VALUES (100,1), (50, 2), (55, 3)
    ) t0
    INNER JOIN (
    SELECT t.* FROM (
        SELECT 
            b.id as book_id,
            b.name as book_name,
            c.id as category_id,
            c.name as category_name,
            b.read_start,
            b.read_finish
        FROM book b
        LEFT JOIN book_category c ON c.id = b.category_id
        ) t1
    )
    )
'''

inner_table_sql = '''SELECT  ROW_NUMBER() OVER( ORDER BY c."ordering", b."ordering") as idx,
        b.id as book_id,
        b.name as book_name,
        c.id as category_id,
        c.name as category_name,
        b.read_start,
        b.read_finish
        FROM book b
        LEFT JOIN book_category c ON c.id = b.category_id
        WHERE read_start is NULL            
        '''