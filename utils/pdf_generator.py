from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.lib import colors
from datetime import datetime


class ClientPDFGenerator:
    """Générateur de PDF pour les clients"""

    @staticmethod
    def export_clients_list(clients, output_path, company_info=None):
        """Exporter la liste des clients en PDF"""
        
        if company_info is None:
            company_info = {
                'name': 'Votre Entreprise',
                'address': 'Adresse',
                'phone': '0123456789',
                'email': 'contact@entreprise.fr'
            }
        
        try:
            # Créer le document
            doc = SimpleDocTemplate(output_path, pagesize=A4)
            story = []
            
            styles = getSampleStyleSheet()
            
            # En-tête du document
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=20,
                textColor=colors.HexColor('#1f4788'),
                spaceAfter=30,
                alignment=TA_CENTER
            )
            
            story.append(Paragraph("Liste des Clients", title_style))
            story.append(Paragraph(f"{company_info['name']}", styles['Normal']))
            story.append(Paragraph(f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}", styles['Normal']))
            story.append(Spacer(1, 0.3*inch))
            
            # Préparer les données du tableau
            clients_data = [['ID', 'Nom', 'Prénom', 'Téléphone', 'Email', 'Ville']]
            
            for client in clients:
                clients_data.append([
                    str(client.get('id', '')),
                    client.get('nom', ''),
                    client.get('prenom', ''),
                    client.get('telephone', '') or '-',
                    client.get('email', '') or '-',
                    client.get('ville', '') or '-'
                ])
            
            # Créer le tableau
            table = Table(clients_data, colWidths=[0.8*inch, 1.5*inch, 1.5*inch, 1.5*inch, 1.8*inch, 1.2*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('ALIGN', (1, 0), (2, -1), 'LEFT'),
                ('ALIGN', (4, 0), (4, -1), 'LEFT'),
                ('ALIGN', (5, 0), (5, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F0F0F0')])
            ]))
            
            story.append(table)
            story.append(Spacer(1, 0.3*inch))
            
            # Résumé
            total_clients = len(clients)
            clients_avec_email = sum(1 for c in clients if c.get('email'))
            clients_avec_telephone = sum(1 for c in clients if c.get('telephone'))
            
            summary_style = ParagraphStyle(
                'Summary',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#666666')
            )
            
            story.append(Spacer(1, 0.2*inch))
            story.append(Paragraph(f"<b>Résumé:</b> Total: {total_clients} clients | Avec email: {clients_avec_email} | Avec téléphone: {clients_avec_telephone}", summary_style))
            story.append(Spacer(1, 0.1*inch))
            story.append(Paragraph(f"<i>Document généré automatiquement le {datetime.now().strftime('%d/%m/%Y à %H:%M')}</i>", summary_style))
            
            # Générer le PDF
            doc.build(story)
            return True, f"PDF généré avec succès : {output_path}"
        except Exception as e:
            return False, f"Erreur lors de la génération du PDF : {str(e)}"

    @staticmethod
    def export_client_details(client, history, stats, output_path, company_info=None):
        """Exporter les détails d'un client en PDF"""
        
        if company_info is None:
            company_info = {
                'name': 'Votre Entreprise',
                'address': 'Adresse',
                'phone': '0123456789',
                'email': 'contact@entreprise.fr'
            }
        
        try:
            # Créer le document
            doc = SimpleDocTemplate(output_path, pagesize=A4)
            story = []
            
            styles = getSampleStyleSheet()
            
            # En-tête
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                textColor=colors.HexColor('#1f4788'),
                spaceAfter=20,
                alignment=TA_CENTER
            )
            
            story.append(Paragraph(f"Fiche Client - {client['nom']} {client['prenom']}", title_style))
            story.append(Spacer(1, 0.2*inch))
            
            # Informations du client
            info_style = ParagraphStyle(
                'Info',
                parent=styles['Normal'],
                fontSize=10
            )
            
            info_text = f"""
            <b>Informations Personnelles:</b><br/>
            Nom: {client.get('nom', 'N/A')} {client.get('prenom', 'N/A')}<br/>
            Téléphone: {client.get('telephone', 'Non renseigné')}<br/>
            Email: {client.get('email', 'Non renseigné')}<br/>
            Adresse: {client.get('adresse', 'Non renseignée')}<br/>
            Ville: {client.get('ville', 'Non renseignée')} {client.get('code_postal', '')}<br/>
            """
            
            story.append(Paragraph(info_text, info_style))
            story.append(Spacer(1, 0.2*inch))
            
            # Statistiques
            if stats:
                stats_text = f"""
                <b>Statistiques:</b><br/>
                Nombre d'achats: {stats.get('nombre_achats', 0)}<br/>
                Chiffre d'affaires total: {float(stats.get('ca_total', 0)):.2f}€<br/>
                Montant moyen par achat: {float(stats.get('montant_moyen', 0)):.2f}€<br/>
                Dernière visite: {stats.get('derniere_visite', 'N/A')}<br/>
                """
                story.append(Paragraph(stats_text, info_style))
                story.append(Spacer(1, 0.2*inch))
            
            # Historique des achats
            if history:
                story.append(Paragraph("<b>Historique des Achats:</b>", styles['Heading3']))
                story.append(Spacer(1, 0.1*inch))
                
                history_data = [['N° Facture', 'Date', 'Montant', 'Statut']]
                
                for item in history:
                    history_data.append([
                        str(item.get('numero_facture', '')),
                        str(item.get('date_vente', ''))[:10],
                        f"{float(item.get('montant_total', 0)):.2f}€",
                        item.get('statut', '')
                    ])
                
                table = Table(history_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#70AD47')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTSIZE', (0, 1), (-1, -1), 9)
                ]))
                
                story.append(table)
            
            story.append(Spacer(1, 0.3*inch))
            story.append(Paragraph(f"<i>Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}</i>", styles['Normal']))
            
            # Générer le PDF
            doc.build(story)
            return True, f"PDF généré avec succès : {output_path}"
        except Exception as e:
            return False, f"Erreur lors de la génération du PDF : {str(e)}"


class InvoiceGenerator:

    @staticmethod
    def generate_invoice(sale, details, payment_history, output_path, company_info=None):
        """Générer une facture PDF"""
        
        if company_info is None:
            company_info = {
                'name': 'Votre Entreprise',
                'address': 'Adresse',
                'phone': '0123456789',
                'email': 'contact@entreprise.fr'
            }
        
        # Créer le document
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        story = []
        
        styles = getSampleStyleSheet()
        
        # En-tête entreprise
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        story.append(Paragraph(company_info['name'], title_style))
        story.append(Paragraph(f"{company_info['address']} | {company_info['phone']} | {company_info['email']}", styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Infos facture
        invoice_info = [
            [
                f"<b>FACTURE</b><br/><b>{sale.get('numero_facture', 'N/A')}</b>",
                f"<b>Date:</b> {str(sale.get('date_vente', ''))[:10]}<br/><b>Client:</b> {sale.get('client_nom', 'N/A')}"
            ]
        ]
        
        table = Table(invoice_info, colWidths=[3*inch, 3*inch])
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
        ]))
        story.append(table)
        story.append(Spacer(1, 0.2*inch))
        
        # Tableau des articles
        articles_data = [['Produit', 'Quantité', 'P. Unit.', 'Total']]
        
        for detail in details:
            articles_data.append([
                detail.get('produit_nom', ''),
                str(detail.get('quantite', '')),
                f"{float(detail.get('prix_unitaire', 0)):.2f}€",
                f"{float(detail.get('sous_total', 0)):.2f}€"
            ])
        
        table = Table(articles_data, colWidths=[3*inch, 1*inch, 1*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(table)
        story.append(Spacer(1, 0.2*inch))
        
        # Totaux
        montant_total = float(sale.get('montant_total', 0))
        montant_paye = float(sale.get('montant_paye', 0))
        montant_reste = montant_total - montant_paye
        
        totals_data = [
            ['', 'Montant total TTC', f'{montant_total:.2f}€'],
            ['', 'Montant payé', f'{montant_paye:.2f}€'],
            ['', '<b>Montant restant</b>', f'<b>{montant_reste:.2f}€</b>']
        ]
        
        table = Table(totals_data, colWidths=[3.5*inch, 1.5*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (1, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (1, 0), (-1, -1), 11),
            ('BACKGROUND', (1, -1), (-1, -1), colors.HexColor('#FFE699')),
            ('GRID', (1, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(table)
        story.append(Spacer(1, 0.3*inch))
        
        # Historique paiements
        if payment_history:
            story.append(Paragraph("<b>Historique des paiements</b>", styles['Heading3']))
            payments_data = [['Date', 'Montant']]
            
            for payment in payment_history:
                payments_data.append([
                    str(payment.get('date_paiement', ''))[:10],
                    f"{float(payment.get('montant', 0)):.2f}€"
                ])
            
            table = Table(payments_data, colWidths=[3.5*inch, 2.5*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E7E6E6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(table)
        
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph(f"Généré le {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
        
        # Générer le PDF
        doc.build(story)
