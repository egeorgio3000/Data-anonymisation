CREATE TABLE IF NOT EXISTS users (
    id_user INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(255) DEFAULT 'Nom',
    prenom VARCHAR(255) DEFAULT 'Prénom',
    civilite VARCHAR(10) DEFAULT 'M',
    img_url VARCHAR(255) DEFAULT 'https://imgurl.com/',
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS products (
    id_product INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) DEFAULT 'Product',
    description TEXT,
    price DECIMAL(10, 2) DEFAULT 3.14,
    img_url VARCHAR(255) DEFAULT 'https://imgurl.com/',
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS orders (
    id_order INT AUTO_INCREMENT PRIMARY KEY,
    id_user INT,
    id_product INT,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_user) REFERENCES users(id_user),
    FOREIGN KEY (id_product) REFERENCES products(id_product)
);

CREATE TABLE IF NOT EXISTS contacts_info (
    id_contact_info INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    address VARCHAR(255) DEFAULT 'Adresse',
    email VARCHAR(255) DEFAULT 'email@email.com',
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id_user)
);

CREATE TABLE IF NOT EXISTS factures (
    id_facture INT AUTO_INCREMENT PRIMARY KEY,
    id_user INT,
    id_test INT DEFAULT 90000,
    facture_email VARCHAR(255) DEFAULT 'facture_email@facture.com',
    facture_address VARCHAR(255) DEFAULT 'facture_address',
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_user) REFERENCES users(id_user)
);

CREATE TABLE IF NOT EXISTS facture_details (
    id_facture_detail INT AUTO_INCREMENT PRIMARY KEY,
    id_facture INT,
    img_url VARCHAR(255) DEFAULT 'https://imgurl.com/',
    description VARCHAR(255) DEFAULT 'description',
    quantity INT DEFAULT 1,
    unit_price DECIMAL(10, 2) DEFAULT 3.14,
    total_price DECIMAL(10, 2) AS (quantity * unit_price),
    date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_facture) REFERENCES factures(id_facture)
);

CREATE TABLE IF NOT EXISTS facture_metadata (
    id_facture_metadata INT AUTO_INCREMENT PRIMARY KEY,
    id_facture INT UNIQUE NOT NULL,
    iban VARCHAR(255) DEFAULT 'iban',
    payment_terms VARCHAR(255) DEFAULT 'payment_terms',
    additional_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (id_facture) REFERENCES factures(id_facture)
);

DELETE FROM users;
DELETE FROM contacts_info;
DELETE FROM factures;
DELETE FROM facture_details;
DELETE FROM facture_metadata;


DELIMITER $$

CREATE PROCEDURE InsertData()
BEGIN
    DECLARE user_id INT;
    DECLARE facture_id INT;
    DECLARE invoice_count INT DEFAULT 2;
    DECLARE detail_count INT DEFAULT 3;
    DECLARE i INT DEFAULT 1;
    DECLARE invoice_num INT;
    DECLARE detail_num INT;

    WHILE i <= 1000 DO
        INSERT INTO users (nom, prenom, civilite, img_url)
        VALUES (CONCAT('Name', i), CONCAT('Surname', i), 'M', 'https://imgurl.com/');
        SET user_id = LAST_INSERT_ID();

        INSERT INTO contacts_info (user_id, address, email)
        VALUES (user_id, CONCAT('Address', i), CONCAT('email', i, '@email.com'));
        
        SET invoice_num = 1;
        WHILE invoice_num <= invoice_count DO
            INSERT INTO factures (id_user, facture_email, facture_address)
            VALUES (user_id, CONCAT('invoice_email', i, '_', invoice_num, '@invoice.com'), CONCAT('invoice_address', i, '_', invoice_num));
            SET facture_id = LAST_INSERT_ID();

            INSERT INTO facture_metadata (id_facture, iban, payment_terms, additional_notes)
            VALUES (facture_id, CONCAT('iban', i, '_', invoice_num), CONCAT('payment_terms', i, '_', invoice_num), CONCAT('additional_notes', i, '_', invoice_num));
            
            SET detail_num = 1;
            WHILE detail_num <= detail_count DO
                INSERT INTO facture_details (id_facture, description, quantity, unit_price)
                VALUES (facture_id, CONCAT('Description', i, '_', detail_num), detail_num, detail_num*10.0);
                SET detail_num = detail_num + 1;
            END WHILE;
            SET invoice_num = invoice_num + 1;
        END WHILE;
        
        INSERT INTO products (name, description, price, img_url)
        VALUES (CONCAT('Product', i), CONCAT('Description', i), i*10.0, CONCAT('https://imgurl.com/', i));

        INSERT INTO orders (id_user, id_product)
        VALUES (user_id, i);

        SET i = i + 1;
    END WHILE;

    INSERT INTO orders (id_user, id_product)
    SELECT id_user, id_product
    FROM users
    CROSS JOIN products
    WHERE RAND() < 0.1 AND id_user > 3;

    INSERT INTO orders (id_user, id_product)
    VALUES (3, 1), (3, 2), (3, 3), (3, 4), (3, 5), (3, 6), (3, 7), (3, 8), (3, 9), (3, 10);
END$$

DELIMITER ;


CALL InsertData();
