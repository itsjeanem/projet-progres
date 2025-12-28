-- Migration: Add mouvements_stock table for stock tracking
-- Run this if you already have an existing database

CREATE TABLE IF NOT EXISTS mouvements_stock(
    id INT AUTO_INCREMENT PRIMARY KEY,
    produit_id INT NOT NULL,
    quantite INT NOT NULL,
    raison VARCHAR(255),
    user_id INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (produit_id) REFERENCES produits(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_produit(produit_id),
    INDEX idx_created(created_at)
) ENGINE=InnoDB;
