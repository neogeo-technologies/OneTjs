# Agrégation automatique

Pour permettre une agrégation automatique à toutes les échelles à partir d’un jeu de données à une échelle donnée il faut :

* décrire les relations spatiales entre les différentes échelles
* indiquer pour chaque attribut des données s’il peut faire l’objet d’une agrégation spatiale et à partir de quel autre champ cet agrégation peut être calculée

Relations spatiales entre référentiels pour chaque année du référentiel :

* Un EPCI est constitué de communes
* Une unité urbaine est constitué de communes
* Un département est constitué de communes
* Une région est constitué de départements
* …

Types d’attributs pouvant faire l’objet d’agrégation :

* nominal : dénomination -> on n’en fait d’agrégation
* ordinal : numéro d'ordre -> on n’en fait d'agrégation
* count : nombre d’entités -> on les agrège par simple addition
* measure : quantité -> on les agrège après pondération avec un autre champ

Traitement des champs de type measure :

* la pondération est effectuée par rapport à un autre attribut du jeu de données
  * la population totale de la commune par exemple
* la pondération est effectuée par rapport à un attribut d’un autre jeu de donnée :
  * la population totale de la commune par exemple
* la pondération est effectuée par rapport à un attribut des entités du référentiel :
  * la superficie de la commune par exemple


## Déclaration des référentiels et de leurs relations

...


## Déclaration des référentiels associés à un jeu de données


...


## Déclaration du mode d'agrégation d'un attribut

Paramètres à utiliser dans le fichier yaml de déclaration d'un jeu de données :
* au niveau de la section "attributes":
** allow_agregation : indique si l'agrégation de l'attribut pour d'autres référentiels est possible. Si cet information
est omise, l'attribut ne faut pas l'objet d'une agrégation
** weighting_attribute_name : nom de l'attribut utilisé pour la pondération effectuée lors de l'agrégation. Si cet
information est omise, cet attribut ne fait pas l'objet d'une agrégation.
** weighting_attribute_source : source de données de l'attribut. Valeurs possibles :
*** "self" : l'attribut provient du même jeu de données [valeur par défaut]
*** "framework" : l'attribut provient du référentiel (framework) natif du jeu de données
*** nom d'un autre jeu de données : l'attribut provient d'un autre jeu de données

Exemple :

```
attributes:
  - name:                       part_des_menages
[...]
    values:                     Measure
    allow_agregation :  yes
    weighting_attribute_name :  nb_menages
    weighting_attribute_source :  self
```
