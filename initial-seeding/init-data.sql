CREATE TABLE "payment_method"(
    "id" SERIAL NOT NULL,
    "by_sepa" INTEGER NOT NULL,
    "by_cb" INTEGER NOT NULL
);
ALTER TABLE
    "payment_method" ADD PRIMARY KEY("id");
CREATE TABLE "cb"(
    "id" SERIAL NOT NULL,
    "cvc" SMALLINT NOT NULL,
    "date" DATE NOT NULL,
    "code" VARCHAR(255) NOT NULL
);
ALTER TABLE
    "cb" ADD PRIMARY KEY("id");
CREATE TABLE "addresses"(
    "id" SERIAL NOT NULL,
    "user_id" INTEGER NOT NULL,
    "address_number" SMALLINT NOT NULL,
    "address" VARCHAR(255) NOT NULL,
    "last_name" VARCHAR(255) NOT NULL,
    "first_name" VARCHAR(255) NOT NULL,
    "zip_code" INTEGER NOT NULL,
    "city" VARCHAR(255) NOT NULL,
    "country" VARCHAR(255) NOT NULL
);
ALTER TABLE
    "addresses" ADD PRIMARY KEY("id");
CREATE TABLE "sepa"(
    "id" SERIAL NOT NULL,
    "bic" VARCHAR(255) NOT NULL,
    "iban" VARCHAR(255) NOT NULL
);
ALTER TABLE
    "sepa" ADD PRIMARY KEY("id");
CREATE TABLE "payment"(
    "id" SERIAL NOT NULL,
    "user_id" INTEGER NOT NULL,
    "payment_method_id" INTEGER NOT NULL
);
ALTER TABLE
    "payment" ADD PRIMARY KEY("id");
CREATE TABLE "users"(
    "id" SERIAL NOT NULL,
    "last_name" VARCHAR(255) NOT NULL,
    "first_name" VARCHAR(255) NOT NULL,
    "email" VARCHAR(255) NOT NULL,
    "password" VARCHAR(255) NOT NULL
);
ALTER TABLE
    "users" ADD PRIMARY KEY("id");
ALTER TABLE
    "payment_method" ADD CONSTRAINT "payment_method_by_sepa_foreign" FOREIGN KEY("by_sepa") REFERENCES "sepa"("id");
ALTER TABLE
    "payment" ADD CONSTRAINT "payment_payment_method_id_foreign" FOREIGN KEY("payment_method_id") REFERENCES "payment_method"("id");
ALTER TABLE
    "payment" ADD CONSTRAINT "payment_user_id_foreign" FOREIGN KEY("user_id") REFERENCES "users"("id");
ALTER TABLE
    "payment_method" ADD CONSTRAINT "payment_method_by_cb_foreign" FOREIGN KEY("by_cb") REFERENCES "cb"("id");
ALTER TABLE
    "addresses" ADD CONSTRAINT "addresses_user_id_foreign" FOREIGN KEY("user_id") REFERENCES "users"("id");


DO $$
DECLARE
    user_id INTEGER;
    payment_method_id INTEGER;
    cb_id INTEGER;
    sepa_id INTEGER;
    address_id INTEGER;
    address_count INTEGER := 3;
    payment_count INTEGER := 2;
BEGIN
    FOR i IN 1..10000 LOOP
        INSERT INTO users (last_name, first_name, email, password)
        VALUES ('LastName'||i, 'FirstName'||i, 'user'||i||'@example.com', 'password'||i) RETURNING id INTO user_id;
        
        FOR j IN 1..address_count LOOP
            INSERT INTO addresses (user_id, address_number, address, last_name, first_name, zip_code, city, country)
            VALUES (user_id, j, 'Street '||j||' User '||i, 'LastName'||i, 'FirstName'||i, 10000 + j, 'City'||i, 'Country'||i);
        END LOOP;
        
        FOR k IN 1..payment_count LOOP
            INSERT INTO cb (cvc, date, code)
            VALUES (123, '2023-12-31', 'Code'||i||'_'||k) RETURNING id INTO cb_id;
            
            INSERT INTO sepa (bic, iban)
            VALUES ('BIC'||i||'_'||k, 'IBAN'||i||'_'||k) RETURNING id INTO sepa_id;
            
            INSERT INTO payment_method (by_sepa, by_cb)
            VALUES (sepa_id, cb_id) RETURNING id INTO payment_method_id;
            
            INSERT INTO payment (user_id, payment_method_id)
            VALUES (user_id, payment_method_id);
        END LOOP;
    END LOOP;
END$$;
