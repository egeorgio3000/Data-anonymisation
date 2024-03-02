CREATE TABLE IF NOT EXISTS users (
    id_user SERIAL PRIMARY KEY,
    nom VARCHAR(255) DEFAULT 'Nom',
    prenom VARCHAR(255) DEFAULT 'Prénom',
    civilite VARCHAR(10) DEFAULT 'M',
    img_url VARCHAR(255) DEFAULT 'https://imgurl.com/',
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS products (
    id_product SERIAL PRIMARY KEY,
    name VARCHAR(255) DEFAULT 'Product',
    description TEXT DEFAULT 'Description',
    price DECIMAL(10, 2) DEFAULT 3.14,
    img_url VARCHAR(255) DEFAULT 'https://imgurl.com/',
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS orders (
    id_order SERIAL PRIMARY KEY,
    id_user INT,
    id_product INT,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_orders_users FOREIGN KEY (id_user) REFERENCES users(id_user),
    CONSTRAINT fk_orders_products FOREIGN KEY (id_product) REFERENCES products(id_product)
);


CREATE TABLE IF NOT EXISTS contacts_info (
    id_contact_info SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id_user),
    address VARCHAR(255) DEFAULT 'Adresse',
    email VARCHAR(255) DEFAULT 'email@email.com',
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS factures (
    id_facture SERIAL PRIMARY KEY,
    id_user INT REFERENCES users(id_user),
    id_test INT DEFAULT 90000,
    facture_email VARCHAR(255) DEFAULT 'facture_email@facture.com',
    facture_address VARCHAR(255) DEFAULT 'facture_address',
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS facture_details (
    id_facture_detail SERIAL PRIMARY KEY,
    id_facture INT REFERENCES factures(id_facture),
    img_url VARCHAR(255) DEFAULT 'https://imgurl.com/',
    description VARCHAR(255) DEFAULT 'description',
    quantity INT DEFAULT 1,
    unit_price DECIMAL(10, 2) DEFAULT 3.14,
    total_price DECIMAL(10, 2) GENERATED ALWAYS AS (quantity * unit_price) STORED,
    date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS facture_metadata (
    id_facture_metadata SERIAL PRIMARY KEY,
    id_facture INT UNIQUE NOT NULL REFERENCES factures(id_facture),
    iban VARCHAR(255) DEFAULT 'iban',
    payment_terms VARCHAR(255) DEFAULT 'payment_terms',
    additional_notes TEXT DEFAULT 'additional_notes',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE FUNCTION calculate_total_price() RETURNS TRIGGER AS $$
BEGIN
    NEW.total_price := NEW.quantity * NEW.unit_price;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER facture_details_before_insert_or_update
BEFORE INSERT OR UPDATE
ON facture_details
FOR EACH ROW
EXECUTE FUNCTION calculate_total_price();

CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_updated_at_before_update
BEFORE UPDATE
ON facture_metadata
FOR EACH ROW
EXECUTE FUNCTION update_modified_column();


DELETE FROM users WHERE 1=1;

ALTER SEQUENCE users_id_user_seq RESTART WITH 1;

DELETE FROM contacts_info WHERE 1=1;

ALTER SEQUENCE contacts_info_id_contact_info_seq RESTART WITH 1;

DELETE FROM factures WHERE 1=1;

ALTER SEQUENCE factures_id_facture_seq RESTART WITH 1;

DELETE FROM facture_details WHERE 1=1;

ALTER SEQUENCE facture_details_id_facture_detail_seq RESTART WITH 1;

DELETE FROM facture_metadata WHERE 1=1;

ALTER SEQUENCE facture_metadata_id_facture_metadata_seq RESTART WITH 1;



DO $$
DECLARE
    user_id integer;
    facture_id integer;
    invoice_count INTEGER := 2;
    detail_count INTEGER := 3;
BEGIN
    FOR i IN 1..1000 LOOP
        INSERT INTO users (nom, prenom, civilite, img_url)
        VALUES ('Name'||i, 'Surname'||i, 'M', 'https://imgurl.com/') RETURNING id_user INTO user_id;

        INSERT INTO contacts_info (user_id, address, email)
        VALUES (user_id, 'Address'||i, 'email'||i||'@email.com');
        
        FOR invoice_num IN 1..invoice_count LOOP
            INSERT INTO factures (id_user, facture_email, facture_address)
            VALUES (user_id, 'invoice_email'||i||'_'||invoice_num||'@invoice.com', 'invoice_address'||i||'_'||invoice_num) RETURNING id_facture INTO facture_id;

            INSERT INTO facture_metadata (id_facture, iban, payment_terms, additional_notes)
            VALUES (facture_id, 'iban'||i||'_'||invoice_num, 'payment_terms'||i||'_'||invoice_num, 'additional_notes'||i||'_'||invoice_num);
            
            FOR detail_num IN 1..detail_count LOOP
                INSERT INTO facture_details (id_facture, description, quantity, unit_price)
                VALUES (facture_id, 'Description'||i||'_'||detail_num, detail_num, detail_num*10.0);
            END LOOP;
        END LOOP;
        

        INSERT INTO products (name, description, price, img_url)
        VALUES ('Product'||i, 'Description'||i, i*10.0, 'https://imgurl.com/'||i);

        INSERT INTO orders (id_user, id_product)
        VALUES (user_id, i);

    END LOOP;
END$$;


INSERT INTO orders (id_user, id_product)
SELECT id_user, id_product
FROM users
CROSS JOIN products
WHERE random() < 0.1 AND id_user > 3;

INSERT INTO orders (id_user, id_product)
VALUES (3, 1), (3, 2), (3, 3), (3, 4), (3, 5), (3, 6), (3, 7), (3, 8), (3, 9), (3, 10)


