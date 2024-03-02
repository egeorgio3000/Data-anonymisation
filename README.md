###### Data Anonymization

# Configuration File Documentation

This document provides comprehensive guidance on the structure and use of the JSON configuration file for data processing scripts. It includes details on specifying tables for processing, defining anonymization types for columns, establishing relationships between tables, caching strategies, and more.

## Running the Script

To execute the data processing script with a configuration file, use the following command in your terminal:

```bash
python3 main.py <configuration_file>.json
```

Replace `<configuration_file>` with the name of your actual configuration file.

## Configuration File Structure

The JSON configuration file allows detailed specification of database tables and columns for processing, including their relationships, caching strategies, and anonymization types.

### Tables

- **`tables`**: An array of objects, each representing a table in the database that needs processing.
  - **`caching`**: Specifies the caching strategy (`reset`, `cache`, `no-cache`).
  - **`name`**: The name of the table.
  - **`id`**: The primary key of the table.
  - **`target_id`** _(optional)_: Specifies the rows to be processed, supporting single IDs, ranges, or combinations thereof (e.g., `1,3,5:100`). If omitted, all rows are processed.
  - **`columns`**: An array of objects detailing columns to be processed or anonymized.
  - **`relations_tables`** _(optional)_ : An array of objects defining relationships to other tables for processing related data. **`relations_tables`** can also contain nested relationships.

### Caching Options

- **`reset`**: Clears any previously processed data and then caches the new results. This option is useful for ensuring the latest data is always processed.
- **`cache`**: Saves processed data and does not update other databases if the data has already been processed. This option helps avoid redundant processing.
- **`no-cache`**: Processes data without using any caching mechanism, always fetching and processing fresh data.

### Columns

Each table can specify columns for processing or anonymization within the `columns` array:

- **`name`**: The name of the column in the table. This directly maps to the column names as defined in the database.
- **`type`**: Specifies the type of processing or anonymization to be applied to the column. The available types include:
  - **`firstname`**: Anonymizes first names with plausible alternatives. Ensures coherence with the `civility` field to maintain logical consistency in gender or formality level.
  - **`lastname`**: Replaces last names with random but plausible last names to protect personal identity.
  - **`civility`**: Adjusts titles or salutations to correspond with the anonymized `firstname`, ensuring the anonymized data maintains logical and social coherence.
  - **`email`**: Generates fictitious but valid-looking email addresses that may incorporate elements from both the `firstname` and `lastname` fields to produce a believable email address that respects the coherence between these fields.
  - **`imgurl`**: Replace URLs of images with placeholders to protect personal images.
  - **`address`**: Substitute real addresses with generic or fictional ones.
  - **`address_number`**:
  - **`address_streetname`**:
  - **`address_zipcode`**:
  - **`address_city`**:
  - **`current_country`**:
  - **`iban`**: Create dummy IBANs that are structurally valid but not linked to real accounts.
  - **`swift`**:Create dummy swift bank code that are structurally valid but not linked to real accounts.
  - **`card_number`**: VISA structure card number
  - **`card_cvc`**: VISA structure card CVC
  - **`card_expiration`**:
  - **`password`**:

This mechanism allows for targeted anonymization or transformation of sensitive data, ensuring privacy and compliance with data protection regulations.

Example of users:

| name   | lastname | civility | email                | imgurl                        | iban                        | swift       |
| ------ | -------- | -------- | -------------------- | ----------------------------- | --------------------------- | ----------- |
| Traore | Victor   | M        | victor.traore@sfr.fr | ttps://dummyimage.com/530x995 | FR1206625227645797821194834 | IBGDFRXD46B |

| address                      | address_number | address_streetname | address_zipcode | address_city | current_country |
| ---------------------------- | -------------- | ------------------ | --------------- | ------------ | --------------- |
| 3, rue de Hardy 80465 Marion | 3              | rue de Hardy       | 80465           | Marion       | France          |

| card_number      | card_cvc | card_expiration | password                                 |
| ---------------- | -------- | --------------- | ---------------------------------------- |
| 4423467996503612 | 804      | 2029-04-01      | d498fcqxn3tb97r4o0ph9qphp4xy9a0wkmddlbn7 |

### Relationships

- **`relations_tables`**: An array of objects defining relationships to other tables for processing related data.
  - **`type`**: The type of relationship (`one_to_one`, `one_to_many`).
  - **`name`**: The name of the related table.
  - **`id`**: The primary key of the related table.
  - **`relation_id`**: The column that establishes the relationship with the parent table.
  - **`parent_relation_id`**: The primary key of the parent table that is related to the child table.
  - **`columns`** _(optional)_ : Specifies columns in the related table to be processed, similar to the parent table's `columns` configuration.

### Relationships Between Tables

- **`relations_tables`**: Defines direct relationships to other tables, specifying how related data should be processed. Relationships are crucial for maintaining data integrity and coherence across related records.

### Relationship Types

- **`one_to_one`**: Each record in the primary table corresponds to one record in the related table.
- **`one_to_many`**: A single record in the primary table may correspond to multiple records in the related table.

### Nested Relationships

After defining direct relationships, the configuration can also specify nested relationships, or relationships of relationships, allowing for comprehensive data processing across multiple related tables.

## Example Configuration

Here's a simplified example of a configuration file specifying a single table with anonymization rules:

```json
{
  "tables": [
    {
      "name": "users",
      "columns": [
        { "name": "lastname", "type": "lastname" },
        { "name": "firstname", "type": "firstname" },
        { "name": "email", "type": "email" },
        { "name": "address", "type": "address" }
      ],
      "relations_tables": [
        {
          "type": "one_to_one",
          "name": "user_profiles",
          "columns": [{ "name": "profile_picture", "type": "imgurl" }]
        }
      ]
    }
  ]
}
```

This configuration outlines how to process the `users` table, including relationships with a `user_profiles` table and specific columns for anonymization.

## Example Configuration multiple relationships

Here's an example configuration file specifying a single table with anonymization rules, direct relationships, and nested relationships:

```json
{
  "tables": [
    {
      "name": "users",
      "target_id": "1,3,5:100",
      "columns": [
        {"name": "lastname", "type": "lastname"},
        {"name": "firstname", "type": "firstname"},
        {"name": "email", "type": "email"},
        {"name": "address", "type": "address"}
      ],
      "relations_tables": [
        {
          "name": "orders",
          "relations_tables": [
            {
              "name": "products",
              "columns": [...]
            }
          ]
        }
      ]
    }
  ]
}
```

This configuration outlines how to process the `users` table, including relationships with an `orders` table, which in turn has relationships with a `products` table. The configuration also specifies specific columns for anonymization.

# Setting Up Environment

To begin setting up your environment for data anonymization, you'll need to create a `.env` file and use Docker Compose. Here are the steps:

#### Create `.env` File

1. Create a new file named `.env` in your project directory.
2. In the `.env` file, define the following environment variables required for your data anonymization project:

   ```
   DATABASE_USER=<your_database_username>
   DATABASE_PASSWORD=<your_database_password>
   DATABASE_DB=<your_database_name>
   DATABASE_HOST=<your_database_host>
   DATABASE_PORT=<your_database_port>
   DATABASE_TYPE=<your_database_type> # if not set, defaults to postgresql

   # not required:
   # DATABASE_TYPE=<your_database_type> # if not set, defaults to postgresql
   # LIMIT_QUERY_COMMIT=100 # if not set, it will be 250
   # LIMIT_QUERY_SELECT=500 # if not set, it will be 1000

   # TIME_QUERY_SELECT=1 # if not set, it will be 0.2
   # TIME_QUERY_COMMIT=1 # if not set, it will be 0.2


   # for testing purposes:
   PGADMIN_DEFAULT_EMAIL=<your_pgadmin_email>
   PGADMIN_DEFAULT_PASSWORD=<your_pgadmin_password>
   ```

   Replace the placeholders with your actual database credentials and PGAdmin details.

#### Using Docker Compose

1. Once your `.env` file is set up with the above variables, you can use Docker Compose to build and run your containers.

   Run the following command in your terminal to build and run your containers:

   ```bash
   docker-compose up --build
   ```

   Run the following command in your terminal to stop and remove your containers and volumes:

   ```bash
   docker-compose down -v
   ```

   or run the following command to stop and remove your containers, volumes, images, and networks:

   ```bash
   docker-compose down -v --rmi all --remove-orphans

   ```

2. This command will use the `docker-compose.yml` file in your project directory, along with the environment variables defined in your `.env` file, to build and start the required services for your data anonymization project.

### Note

Ensure that Docker and Docker Compose are installed on your machine and that the `docker-compose.yml` file is correctly set up in your project directory before running the above commands.
