-- Base de donnees
CREATE DATABASE IF NOT EXISTS gestion_commerciale 
CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE gestion_commerciale;

-- Table users
CREATE TABLE users(
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin','manager','vendeur') NOT NULL DEFAULT 'vendeur',
    email VARCHAR(100) UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username(username),
    INDEX idx_role(role)
) ENGINE=InnoDB;

-- Table clients
CREATE TABLE clients(
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    telephone VARCHAR(20),
    email VARCHAR(100),
    adresse TEXT,
    ville VARCHAR(100),
    code_postal VARCHAR(10),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_nom(nom),
    INDEX idx_telephone(telephone),
    FULLTEXT idx_search(nom, prenom, email)
) ENGINE=InnoDB;

-- Table categories
CREATE TABLE categories(
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Table produits
CREATE TABLE produits(
    id INT AUTO_INCREMENT PRIMARY KEY,
    category_id INT NOT NULL,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    prix_achat DECIMAL(10,2) NOT NULL,
    prix_vente DECIMAL(10,2) NOT NULL,
    stock_min INT DEFAULT 5,
    stock_actuel INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE RESTRICT,
    INDEX idx_category(category_id),
    INDEX idx_stock(stock_actuel),
    FULLTEXT idx_search(nom, description)
) ENGINE=InnoDB;

-- Table ventes
CREATE TABLE ventes(
    id INT AUTO_INCREMENT PRIMARY KEY,
    numero_facture VARCHAR(50) UNIQUE NOT NULL,
    client_id INT NOT NULL,
    user_id INT NOT NULL,
    date_vente DATETIME DEFAULT CURRENT_TIMESTAMP,
    montant_total DECIMAL(10,2) NOT NULL,
    montant_paye DECIMAL(10,2) DEFAULT 0,
    montant_reste DECIMAL(10,2) GENERATED ALWAYS AS (montant_total - montant_paye) STORED,
    statut ENUM('en_cours','payee','partielle','annulee') DEFAULT 'en_cours',
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE RESTRICT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE RESTRICT,
    INDEX idx_client(client_id),
    INDEX idx_user(user_id),
    INDEX idx_date(date_vente),
    INDEX idx_statut(statut),
    INDEX idx_numero(numero_facture)
) ENGINE=InnoDB;

-- Table ventes_details
CREATE TABLE ventes_details(
    id INT AUTO_INCREMENT PRIMARY KEY,
    vente_id INT NOT NULL,
    produit_id INT NOT NULL,
    quantite INT NOT NULL,
    prix_unitaire DECIMAL(10,2) NOT NULL,
    sous_total DECIMAL(10,2) GENERATED ALWAYS AS (quantite * prix_unitaire) STORED,
    FOREIGN KEY (vente_id) REFERENCES ventes(id) ON DELETE CASCADE,
    FOREIGN KEY (produit_id) REFERENCES produits(id) ON DELETE RESTRICT,
    INDEX idx_vente(vente_id),
    INDEX idx_produit(produit_id)
) ENGINE=InnoDB;

-- Table mouvements_stock
CREATE TABLE mouvements_stock(
    id INT AUTO_INCREMENT PRIMARY KEY,
    produit_id INT NOT NULL,
    user_id INT NOT NULL,
    type ENUM('entree','sortie','ajustement','vente') NOT NULL,
    quantite INT NOT NULL,
    date_mouvement DATETIME DEFAULT CURRENT_TIMESTAMP,
    description TEXT,
    FOREIGN KEY (produit_id) REFERENCES produits(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE RESTRICT,
    INDEX idx_produit(produit_id),
    INDEX idx_date(date_mouvement),
    INDEX idx_type(type)
) ENGINE=InnoDB;

-- Table parametres
CREATE TABLE parametres(
    id INT AUTO_INCREMENT PRIMARY KEY,
    cle VARCHAR(100) UNIQUE NOT NULL,
    valeur TEXT NOT NULL,
    description TEXT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Trigger pour mise a jour stock apres vente
DELIMITER //
CREATE TRIGGER after_vente_insert
    AFTER INSERT ON ventes_details
    FOR EACH ROW
BEGIN
    UPDATE produits
    SET stock_actuel = stock_actuel - NEW.quantite
    WHERE id = NEW.produit_id;

    INSERT INTO mouvements_stock (produit_id, user_id, type, quantite, description)
    SELECT
        NEW.produit_id,
        v.user_id,
        'vente',
        NEW.quantite,
        CONCAT('Vente facture: ', v.numero_facture)
    FROM ventes v
    WHERE v.id = NEW.vente_id;
END//
DELIMITER ;

-- Vues utiles
CREATE VIEW vue_produits_alertes AS
SELECT
    p.id,
    p.nom,
    c.nom AS categorie,
    p.stock_actuel,
    p.stock_min
FROM produits p
JOIN categories c ON p.category_id = c.id
WHERE p.stock_actuel <= p.stock_min;

CREATE VIEW vue_ventes_resume AS
SELECT
    v.id,
    v.numero_facture,
    CONCAT(c.nom, ' ', c.prenom) AS client,
    u.username AS vendeur,
    v.date_vente,
    v.montant_total,
    v.montant_paye,
    v.montant_reste,
    v.statut
FROM ventes v
JOIN clients c ON v.client_id = c.id
JOIN users u ON v.user_id = u.id;