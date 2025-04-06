# Patterns Système: Composant Eltako pour Home Assistant

## Architecture Système
Le composant Eltako s'intègre dans Home Assistant en suivant le modèle d'intégration standard:
1. Découverte et configuration via config_flow
2. Communication avec le matériel via la classe Dongle
3. Représentation des appareils via des entités (lights, covers, binary_sensors)
4. Gestion des événements via le bus d'événements de Home Assistant

## Modèles de Conception Clés
1. **Pattern Entity-Platform**: Chaque type d'appareil (lumière, volet) est implémenté comme une entité distincte
2. **Pattern Observer**: Les entités s'abonnent aux événements du dongle pour recevoir les mises à jour d'état
3. **Pattern Command**: Traduction des actions Home Assistant en commandes pour les appareils Eltako
4. **Pattern Repository**: Gestion centralisée des entités et de leurs états

## Structure des Composants
```
homeassistant_eltako/
├── __init__.py            # Point d'entrée de l'intégration
├── config_flow.py         # Flux de configuration
├── const.py               # Constantes
├── dongle.py              # Communication avec le transceiver
├── binary_sensor.py       # Entités de capteur binaire
├── light.py               # Entités d'éclairage
├── cover.py               # Entités de volet
└── utils.py               # Fonctions utilitaires
```

## Flux de Données
1. **Entrée**: Les messages radio sont reçus par le dongle USB
2. **Traitement**: Le dongle décode les messages et les envoie au bus d'événements
3. **Distribution**: Les entités concernées reçoivent les événements et mettent à jour leur état
4. **Sortie**: Les commandes des utilisateurs sont traduites en messages radio et envoyées par le dongle

## Décisions Techniques Majeures
1. Utilisation d'un modèle de communication asynchrone pour la stabilité
2. Séparation claire entre la communication matérielle et la logique métier
3. Flexibilité pour ajouter de nouveaux types d'appareils
4. Gestion explicite des IDs et des processus de teach-in 