-- PostgreSQL DML for Edge and Node tables
-- Large dataset (10MB) for testing and development
-- Node types: User, Product, Session
-- Edge types: Viewed, Bought

-- This script generates approximately 10MB of data using procedural SQL
-- The data includes realistic e-commerce user behavior patterns

-- Skip data generation if data already exists
DO $$
BEGIN
    IF (SELECT COUNT(*) FROM node) > 0 THEN
        RAISE NOTICE 'Data already exists. Skipping data generation.';
        RETURN;
    END IF;
END $$;

DO $$
DECLARE
user_counter INT := 1;
    product_counter INT := 1;
    session_counter INT := 1;
    edge_counter INT := 1;
    user_id UUID;
    product_id UUID;
    session_id UUID;
    i INT;
    j INT;
    k INT;
    random_price NUMERIC;
    random_stock INT;
    random_age INT;
    random_duration INT;
    random_quantity INT;
    timestamp_val TIMESTAMP;
    user_ids UUID[];
    product_ids UUID[];
    session_ids UUID[];
BEGIN
    -- Generate 2000 User nodes
    RAISE NOTICE 'Generating Users...';
FOR i IN 1..2000 LOOP
        user_id := uuid_generate_v7();
        user_ids := array_append(user_ids, user_id);
        random_age := 18 + floor(random() * 62)::int;

INSERT INTO node (id, label, properties, tags, text_content, summary, metadata) VALUES (
                                                                                           user_id,
                                                                                           'User',
                                                                                           jsonb_build_object(
                                                                                                   'user_id', jsonb_build_object('name', 'user_id', 'data_type', 'string', 'value', 'U' || lpad(i::text, 6, '0')),
                                                                                                   'username', jsonb_build_object('name', 'username', 'data_type', 'string', 'value', 'user_' || md5(random()::text)),
                                                                                                   'email', jsonb_build_object('name', 'email', 'data_type', 'string', 'value', 'user' || i || '@example.com'),
                                                                                                   'age', jsonb_build_object('name', 'age', 'data_type', 'int', 'value', random_age::text),
                                                                                                   'premium', jsonb_build_object('name', 'premium', 'data_type', 'boolean', 'value', (random() > 0.7)::text),
                                                                                                   'registration_date', jsonb_build_object('name', 'registration_date', 'data_type', 'datetime', 'value', (TIMESTAMP '2023-01-01' + (random() * (TIMESTAMP '2026-02-01' - TIMESTAMP '2023-01-01')))::text),
                                                                                                   'total_purchases', jsonb_build_object('name', 'total_purchases', 'data_type', 'int', 'value', floor(random() * 50)::text),
                                                                                                   'total_spent', jsonb_build_object('name', 'total_spent', 'data_type', 'double', 'value', (random() * 5000)::numeric(10,2)::text),
                                                                                                   'loyalty_points', jsonb_build_object('name', 'loyalty_points', 'data_type', 'int', 'value', floor(random() * 10000)::text)
                                                                                           ),
                                                                                           jsonb_build_object(
                                                                                                   'account_type', CASE WHEN random() > 0.7 THEN 'premium' ELSE 'standard' END,
                                                                                                   'status', 'active',
                                                                                                   'country', (ARRAY['US', 'UK', 'CA', 'AU', 'DE', 'FR', 'JP', 'BR', 'IN', 'MX'])[floor(random() * 10 + 1)],
                                                                                                   'segment', (ARRAY['high_value', 'regular', 'occasional', 'new'])[floor(random() * 4 + 1)]
                                                                                           ),
                                                                                           'User ' || 'user_' || md5(random()::text) || ' aged ' || random_age || ', ' ||
                                                                                           CASE WHEN random() > 0.7 THEN 'premium' ELSE 'standard' END || ' account member from ' ||
                                                                                           (ARRAY['US', 'UK', 'CA', 'AU', 'DE', 'FR', 'JP', 'BR', 'IN', 'MX'])[floor(random() * 10 + 1)] ||
            '. Total purchases: ' || floor(random() * 50) || ', loyalty points: ' || floor(random() * 10000) || '.',
                                                                                           'E-commerce customer aged ' || random_age || ' with ' || CASE WHEN random() > 0.7 THEN 'premium' ELSE 'standard' END || ' account status',
                                                                                           jsonb_build_object(
                                                                                                   'entity_type', 'customer',
                                                                                                   'created_by', 'data_generator',
                                                                                                   'version', '1.0',
                                                                                                   'confidence', random()
                                                                                           )
                                                                                       );
END LOOP;

    -- Generate 5000 Product nodes
    RAISE NOTICE 'Generating Products...';
FOR i IN 1..5000 LOOP
        product_id := uuid_generate_v7();
        product_ids := array_append(product_ids, product_id);
        random_price := (random() * 1000 + 5)::numeric(10,2);
        random_stock := floor(random() * 1000)::int;

INSERT INTO node (id, label, properties, tags, text_content, summary, metadata) VALUES (
                                                                                           product_id,
                                                                                           'Product',
                                                                                           jsonb_build_object(
                                                                                                   'product_id', jsonb_build_object('name', 'product_id', 'data_type', 'string', 'value', 'P' || lpad(i::text, 6, '0')),
                                                                                                   'sku', jsonb_build_object('name', 'sku', 'data_type', 'string', 'value', 'SKU-' || upper(md5(i::text))),
                                                                                                   'name', jsonb_build_object('name', 'name', 'data_type', 'string', 'value', 'Product ' || i || ' - ' || (ARRAY['Elite', 'Pro', 'Premium', 'Standard', 'Basic', 'Advanced', 'Ultimate', 'Classic'])[floor(random() * 8 + 1)]),
                                                                                                   'description', jsonb_build_object('name', 'description', 'data_type', 'string', 'value', 'High quality ' || (ARRAY['electronic', 'fashion', 'home', 'sports', 'beauty', 'toy', 'book', 'food'])[floor(random() * 8 + 1)] || ' product with excellent features and durability'),
                                                                                                   'price', jsonb_build_object('name', 'price', 'data_type', 'double', 'value', random_price::text),
                                                                                                   'cost', jsonb_build_object('name', 'cost', 'data_type', 'double', 'value', (random_price * 0.6)::numeric(10,2)::text),
                                                                                                   'stock', jsonb_build_object('name', 'stock', 'data_type', 'int', 'value', random_stock::text),
                                                                                                   'in_stock', jsonb_build_object('name', 'in_stock', 'data_type', 'boolean', 'value', (random_stock > 0)::text),
                                                                                                   'rating', jsonb_build_object('name', 'rating', 'data_type', 'double', 'value', (random() * 2 + 3)::numeric(3,2)::text),
                                                                                                   'review_count', jsonb_build_object('name', 'review_count', 'data_type', 'int', 'value', floor(random() * 1000)::text),
                                                                                                   'weight_kg', jsonb_build_object('name', 'weight_kg', 'data_type', 'double', 'value', (random() * 10)::numeric(5,2)::text),
                                                                                                   'release_date', jsonb_build_object('name', 'release_date', 'data_type', 'date', 'value', (DATE '2020-01-01' + floor(random() * 1500)::int)::text)
                                                                                           ),
                                                                                           jsonb_build_object(
                                                                                                   'category', (ARRAY['Electronics', 'Fashion', 'Home & Garden', 'Sports', 'Beauty', 'Toys', 'Books', 'Food'])[floor(random() * 8 + 1)],
                                                                                                   'subcategory', (ARRAY['Premium', 'Budget', 'Mid-range', 'Luxury'])[floor(random() * 4 + 1)],
                                                                                                   'brand', 'Brand-' || (floor(random() * 100 + 1)::int),
                                                                                                   'featured', (random() > 0.8)::text,
                                                                                                   'on_sale', (random() > 0.7)::text
                                                                                           ),
                                                                                           'Product ' || i || ' - ' || (ARRAY['Elite', 'Pro', 'Premium', 'Standard', 'Basic', 'Advanced', 'Ultimate', 'Classic'])[floor(random() * 8 + 1)] ||
            ': High quality ' || (ARRAY['electronic', 'fashion', 'home', 'sports', 'beauty', 'toy', 'book', 'food'])[floor(random() * 8 + 1)] ||
            ' product with excellent features and durability. ' ||
            'Price: $' || random_price || ', Stock: ' || random_stock || ', Rating: ' || (random() * 2 + 3)::numeric(3,2) || '/5 (' || floor(random() * 1000) || ' reviews). ' ||
            'Category: ' || (ARRAY['Electronics', 'Fashion', 'Home & Garden', 'Sports', 'Beauty', 'Toys', 'Books', 'Food'])[floor(random() * 8 + 1)] ||
            ', Brand: Brand-' || (floor(random() * 100 + 1)::int) || '. ' ||
            CASE WHEN random() > 0.8 THEN 'Featured product. ' ELSE '' END ||
            CASE WHEN random() > 0.7 THEN 'Currently on sale! ' ELSE '' END,
                                                                                           'Product ' || i || ' - ' || (ARRAY['Elite', 'Pro', 'Premium', 'Standard', 'Basic', 'Advanced', 'Ultimate', 'Classic'])[floor(random() * 8 + 1)] ||
            ' priced at $' || random_price || ' with ' || (random() * 2 + 3)::numeric(3,2) || '/5 rating',
                                                                                           jsonb_build_object(
                                                                                                   'entity_type', 'product',
                                                                                                   'created_by', 'data_generator',
                                                                                                   'version', '1.0',
                                                                                                   'confidence', random(),
                                                                                                   'last_updated', CURRENT_TIMESTAMP
                                                                                           )
                                                                                       );
END LOOP;

    -- Generate 8000 Session nodes
    RAISE NOTICE 'Generating Sessions...';
FOR i IN 1..8000 LOOP
        session_id := uuid_generate_v7();
        session_ids := array_append(session_ids, session_id);
        timestamp_val := TIMESTAMP '2025-01-01' + (random() * (TIMESTAMP '2026-02-16' - TIMESTAMP '2025-01-01'));

INSERT INTO node (id, label, properties, tags, text_content, summary, metadata) VALUES (
                                                                                           session_id,
                                                                                           'Session',
                                                                                           jsonb_build_object(
                                                                                                   'session_id', jsonb_build_object('name', 'session_id', 'data_type', 'string', 'value', 'S' || lpad(i::text, 6, '0')),
                                                                                                   'user_id', jsonb_build_object('name', 'user_id', 'data_type', 'string', 'value', 'U' || lpad((floor(random() * 2000 + 1)::int)::text, 6, '0')),
                                                                                                   'start_time', jsonb_build_object('name', 'start_time', 'data_type', 'datetime', 'value', timestamp_val::text),
                                                                                                   'end_time', jsonb_build_object('name', 'end_time', 'data_type', 'datetime', 'value', (timestamp_val + (random() * interval '2 hours'))::text),
                                                                                                   'duration_seconds', jsonb_build_object('name', 'duration_seconds', 'data_type', 'int', 'value', floor(random() * 7200)::text),
                                                                                                   'page_views', jsonb_build_object('name', 'page_views', 'data_type', 'int', 'value', floor(random() * 50 + 1)::text),
                                                                                                   'converted', jsonb_build_object('name', 'converted', 'data_type', 'boolean', 'value', (random() > 0.7)::text),
                                                                                                   'bounce', jsonb_build_object('name', 'bounce', 'data_type', 'boolean', 'value', (random() > 0.6)::text)
                                                                                           ),
                                                                                           jsonb_build_object(
                                                                                                   'device', (ARRAY['desktop', 'mobile', 'tablet'])[floor(random() * 3 + 1)],
                                                                                                   'browser', (ARRAY['Chrome', 'Firefox', 'Safari', 'Edge', 'Opera'])[floor(random() * 5 + 1)],
                                                                                                   'os', (ARRAY['Windows', 'macOS', 'Linux', 'iOS', 'Android'])[floor(random() * 5 + 1)],
                                                                                                   'referrer', (ARRAY['google', 'facebook', 'direct', 'email', 'instagram', 'twitter'])[floor(random() * 6 + 1)]
                                                                                           ),
                                                                                           'User session S' || lpad(i::text, 6, '0') || ' on ' || (ARRAY['desktop', 'mobile', 'tablet'])[floor(random() * 3 + 1)] ||
            ' device using ' || (ARRAY['Chrome', 'Firefox', 'Safari', 'Edge', 'Opera'])[floor(random() * 5 + 1)] || ' browser. ' ||
            'Duration: ' || floor(random() * 7200) || ' seconds, ' || floor(random() * 50 + 1) || ' page views. ' ||
            CASE WHEN random() > 0.7 THEN 'Session resulted in conversion. ' ELSE 'No conversion. ' END ||
            'Referrer: ' || (ARRAY['google', 'facebook', 'direct', 'email', 'instagram', 'twitter'])[floor(random() * 6 + 1)] || '.',
                                                                                           'Session on ' || (ARRAY['desktop', 'mobile', 'tablet'])[floor(random() * 3 + 1)] || ' with ' || floor(random() * 50 + 1) || ' page views',
                                                                                           jsonb_build_object(
                                                                                                   'entity_type', 'session',
                                                                                                   'created_by', 'data_generator',
                                                                                                   'version', '1.0',
                                                                                                   'session_start', timestamp_val
                                                                                           )
                                                                                       );
END LOOP;

    -- Generate Viewed edges (approximately 30,000 edges)
    RAISE NOTICE 'Generating Viewed edges...';
FOR i IN 1..30000 LOOP
        -- Each user views multiple products
        user_id := user_ids[floor(random() * 2000 + 1)];
        product_id := product_ids[floor(random() * 5000 + 1)];
        session_id := session_ids[floor(random() * 8000 + 1)];
        random_duration := floor(random() * 600 + 5)::int;
        timestamp_val := TIMESTAMP '2025-01-01' + (random() * (TIMESTAMP '2026-02-16' - TIMESTAMP '2025-01-01'));

INSERT INTO edge (id, source_id, target_id, label, properties, tags, weight, context, metadata) VALUES (
                                                                                                           uuid_generate_v7(),
                                                                                                           user_id,
                                                                                                           product_id,
                                                                                                           'Viewed',
                                                                                                           jsonb_build_object(
                                                                                                                   'session_id', session_id::text,
                                                                                                                   'timestamp', jsonb_build_object('name', 'timestamp', 'data_type', 'datetime', 'value', timestamp_val::text),
                                                                                                                   'duration_seconds', jsonb_build_object('name', 'duration_seconds', 'data_type', 'int', 'value', random_duration::text),
                                                                                                                   'scroll_depth', jsonb_build_object('name', 'scroll_depth', 'data_type', 'double', 'value', (random() * 100)::numeric(5,2)::text),
                                                                                                                   'clicked_images', jsonb_build_object('name', 'clicked_images', 'data_type', 'int', 'value', floor(random() * 10)::text),
                                                                                                                   'added_to_cart', jsonb_build_object('name', 'added_to_cart', 'data_type', 'boolean', 'value', (random() > 0.8)::text),
                                                                                                                   'added_to_wishlist', jsonb_build_object('name', 'added_to_wishlist', 'data_type', 'boolean', 'value', (random() > 0.85)::text)
                                                                                                           ),
                                                                                                           jsonb_build_object(
                                                                                                                   'interaction_type', 'view',
                                                                                                                   'device', (ARRAY['desktop', 'mobile', 'tablet'])[floor(random() * 3 + 1)],
                                                                                                                   'source', (ARRAY['search', 'category', 'recommendation', 'direct', 'advertisement'])[floor(random() * 5 + 1)]
                                                                                                           ),
                                                                                                           (random_duration / 600.0)::float,  -- Weight based on engagement duration (normalized)
                                                                                                           'User viewed product for ' || random_duration || ' seconds with ' || (random() * 100)::numeric(5,2) || '% scroll depth on ' ||
            (ARRAY['desktop', 'mobile', 'tablet'])[floor(random() * 3 + 1)] || ' device via ' ||
            (ARRAY['search', 'category', 'recommendation', 'direct', 'advertisement'])[floor(random() * 5 + 1)] || ' channel',
                                                                                                           jsonb_build_object(
                                                                                                                   'interaction_type', 'product_view',
                                                                                                                   'engagement_score', (random_duration / 600.0),
                                                                                                                   'created_by', 'data_generator',
                                                                                                                   'timestamp', timestamp_val
                                                                                                           )
                                                                                                       );
END LOOP;

    -- Generate Bought edges (approximately 12,000 edges)
    RAISE NOTICE 'Generating Bought edges...';
FOR i IN 1..12000 LOOP
        user_id := user_ids[floor(random() * 2000 + 1)];
        product_id := product_ids[floor(random() * 5000 + 1)];
        session_id := session_ids[floor(random() * 8000 + 1)];
        random_quantity := floor(random() * 5 + 1)::int;
        random_price := (random() * 1000 + 5)::numeric(10,2);
        timestamp_val := TIMESTAMP '2025-01-01' + (random() * (TIMESTAMP '2026-02-16' - TIMESTAMP '2025-01-01'));

INSERT INTO edge (id, source_id, target_id, label, properties, tags, weight, context, metadata) VALUES (
                                                                                                           uuid_generate_v7(),
                                                                                                           user_id,
                                                                                                           product_id,
                                                                                                           'Bought',
                                                                                                           jsonb_build_object(
                                                                                                                   'session_id', session_id::text,
                                                                                                                   'order_id', jsonb_build_object('name', 'order_id', 'data_type', 'string', 'value', 'ORD-' || lpad(i::text, 8, '0')),
                                                                                                                   'timestamp', jsonb_build_object('name', 'timestamp', 'data_type', 'datetime', 'value', timestamp_val::text),
                                                                                                                   'quantity', jsonb_build_object('name', 'quantity', 'data_type', 'int', 'value', random_quantity::text),
                                                                                                                   'unit_price', jsonb_build_object('name', 'unit_price', 'data_type', 'double', 'value', random_price::text),
                                                                                                                   'total_price', jsonb_build_object('name', 'total_price', 'data_type', 'double', 'value', (random_price * random_quantity)::numeric(10,2)::text),
                                                                                                                   'discount_applied', jsonb_build_object('name', 'discount_applied', 'data_type', 'boolean', 'value', (random() > 0.6)::text),
                                                                                                                   'discount_amount', jsonb_build_object('name', 'discount_amount', 'data_type', 'double', 'value', (random() * random_price * 0.3)::numeric(10,2)::text),
                                                                                                                   'shipping_cost', jsonb_build_object('name', 'shipping_cost', 'data_type', 'double', 'value', (random() * 20)::numeric(10,2)::text),
                                                                                                                   'tax_amount', jsonb_build_object('name', 'tax_amount', 'data_type', 'double', 'value', (random_price * random_quantity * 0.08)::numeric(10,2)::text),
                                                                                                                   'payment_method', jsonb_build_object('name', 'payment_method', 'data_type', 'string', 'value', (ARRAY['credit_card', 'debit_card', 'paypal', 'apple_pay', 'google_pay', 'bank_transfer'])[floor(random() * 6 + 1)]),
                                                                                                                   'shipped', jsonb_build_object('name', 'shipped', 'data_type', 'boolean', 'value', (random() > 0.2)::text),
                                                                                                                   'delivered', jsonb_build_object('name', 'delivered', 'data_type', 'boolean', 'value', (random() > 0.3)::text)
                                                                                                           ),
                                                                                                           jsonb_build_object(
                                                                                                                   'transaction_type', 'purchase',
                                                                                                                   'fulfillment_status', (ARRAY['pending', 'processing', 'shipped', 'delivered', 'cancelled'])[floor(random() * 5 + 1)],
                                                                                                                   'return_eligible', (random() > 0.5)::text,
                                                                                                                   'gift_wrap', (random() > 0.9)::text
                                                                                                           ),
                                                                                                           2.0 + (random_price * random_quantity / 100.0)::float,  -- Higher weight for purchases, scaled by value
                                                                                                           'User purchased ' || random_quantity || ' unit(s) of product for $' || (random_price * random_quantity)::numeric(10,2) ||
            ' using ' || (ARRAY['credit_card', 'debit_card', 'paypal', 'apple_pay', 'google_pay', 'bank_transfer'])[floor(random() * 6 + 1)] ||
            '. Order status: ' || (ARRAY['pending', 'processing', 'shipped', 'delivered', 'cancelled'])[floor(random() * 5 + 1)],
                                                                                                           jsonb_build_object(
                                                                                                                   'interaction_type', 'purchase',
                                                                                                                   'transaction_value', (random_price * random_quantity)::numeric(10,2),
                                                                                                                   'created_by', 'data_generator',
                                                                                                                   'timestamp', timestamp_val,
                                                                                                                   'order_id', 'ORD-' || lpad(i::text, 8, '0')
                                                                                                           )
                                                                                                       );
END LOOP;

    RAISE NOTICE 'Data generation complete!';
    RAISE NOTICE 'Generated: 2000 Users, 5000 Products, 8000 Sessions';
    RAISE NOTICE 'Generated: ~30000 Viewed edges, ~12000 Bought edges';
END $$;

-- Verification queries

-- Count nodes by label
SELECT label, COUNT(*) as count FROM node GROUP BY label ORDER BY label;

-- Count edges by label
SELECT label, COUNT(*) as count FROM edge GROUP BY label ORDER BY label;

-- Show sample User node
SELECT id, label, properties->>'user_id' as user_id, tags FROM node WHERE label = 'User' LIMIT 1;

-- Show sample Product node
SELECT id, label, properties->>'product_id' as product_id, tags FROM node WHERE label = 'Product' LIMIT 1;

-- Show sample Session node
SELECT id, label, properties->>'session_id' as session_id, tags FROM node WHERE label = 'Session' LIMIT 1;

-- Show user purchase and view statistics
SELECT
    n.label as user_label,
    COUNT(CASE WHEN e.label = 'Viewed' THEN 1 END) as total_views,
    COUNT(CASE WHEN e.label = 'Bought' THEN 1 END) as total_purchases
FROM node n
         LEFT JOIN edge e ON n.id = e.source_id
WHERE n.label = 'User'
GROUP BY n.id, n.label
    LIMIT 10;

-- Show most viewed products
SELECT
    n.properties->>'product_id' as product_id,
    n.properties->'name'->>'value' as product_name,
    COUNT(e.id) as view_count
FROM node n
    JOIN edge e ON n.id = e.target_id
WHERE n.label = 'Product' AND e.label = 'Viewed'
GROUP BY n.id, n.properties
ORDER BY view_count DESC
    LIMIT 10;

-- Show most purchased products
SELECT
    n.properties->>'product_id' as product_id,
    n.properties->'name'->>'value' as product_name,
    COUNT(e.id) as purchase_count,
    SUM((e.properties->'total_price'->>'value')::numeric) as total_revenue
FROM node n
    JOIN edge e ON n.id = e.target_id
WHERE n.label = 'Product' AND e.label = 'Bought'
GROUP BY n.id, n.properties
ORDER BY purchase_count DESC
    LIMIT 10;

