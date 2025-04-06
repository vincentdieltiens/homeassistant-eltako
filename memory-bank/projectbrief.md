# Composant Eltako pour Home Assistant

## Objectif du Projet
Ce composant vise à permettre le contrôle des appareils Eltako (F4SR14, FSB14, FUD14) dans Home Assistant. Il s'agit d'une intégration personnalisée qui permet aux utilisateurs de Home Assistant d'interagir avec leur système domotique Eltako.

## Inspiration et Sources
Le projet est inspiré par :
- Le composant Eltako personnalisé (https://gitlab.com/chrysn/home-assistant-eltako)
- La bibliothèque Eltakobus (https://gitlab.com/chrysn/eltakobus)
- Le composant EnOcean par kipe (https://github.com/kipe/enocean)

## Appareils Supportés
Actuellement, le composant prend en charge :
- F4SR14 (Éclairage Simple)
- FUD14 (Variateur)
- FSB14 (Volet Roulant)

## Prérequis Techniques
1. Transceiver externe (USB300 ou "EnOcean PI") pour la communication
2. Système de "teach-in" pour l'appairage des appareils
3. Gestion des ID uniques pour chaque élément
4. Configuration des interrupteurs virtuels avec ID de base + offset

## Contraintes Techniques
- Pas de découverte automatique des appareils
- Nécessité de configurer manuellement les ID des appareils
- Les interrupteurs physiques ne peuvent pas être enregistrés directement dans HA
- Plage d'offset limitée [0, 128] pour les interrupteurs virtuels

## Objectifs de Développement
1. Maintenir la stabilité du composant existant
2. Faciliter l'ajout de nouveaux types d'appareils
3. Améliorer la documentation et l'expérience utilisateur
4. Encourager la contribution de la communauté

## Public Cible
- Utilisateurs de Home Assistant
- Propriétaires d'appareils Eltako
- Développeurs souhaitant contribuer au projet