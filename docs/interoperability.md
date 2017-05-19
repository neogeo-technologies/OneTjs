# Interopérabilté avec d'autres solutions

## Géoclip

Les applications Géoclip semblent utiliser des URI de référentiels classiques connues d'elles-seules.
Exemple : "com" pour le maillage communal frnaçais.

Pour assurer un niveau d'interopérabilité suffisant avec Géoclip pour la découverte des référentiels (frameworks),
il semble utile de pouvoir définir des alias pour les référentiels. Ainsi un même référentiel pourrait être connu sous
de multiples identifiants.


Questions à poser à Emc3 :

* pourquoi certaines requêtes envoyées par le client Géoclip au serveur Géoclip renvoient une erreur 403 ?
Exemple : curl 'https://geoterritoires.hautsdefrance.fr/GC_tjs_client.php' -H 'Host: geoterritoires.hautsdefrance.fr'
-H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:53.0) Gecko/20100101 Firefox/53.0'
-H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
-H 'Accept-Language: fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3' --compressed
-H 'Cookie: PHPSESSID=clgbu209obd7jnv2tkbalt2285' -H 'DNT: 1'
-H 'Connection: keep-alive'
--data 'request=DescribeFrameworks&language=fr&lang=fr&url=http%3A%2F%2Fgeopicardie%2Eneogeo%2Efr%2Fsimple%2Dtjs%2Ftjs%2Fregion%5Fhdf'
S'agit-il d'erreurs indépendantes de Géoclip ?

* comment Géoclip identifie qu'un référentiel est compatible ou non avec la vue courante ?
Je soupçonne que les paramètres supplémentaires inclus dans les requêtes TJS ont pour but d'identifier les référentiels
qui possèdent des enregistrements avec des identifiants présents dans le référentiel courant.

* à quoi servent les paramètres supplémentaires envoyés par Géoclip aux services TJS externes ?
Servent-ils à identifier quels référentiels sont compatibles avec la vue courante ?

* à quoi servent les éléments supplémentaires insérés par Géoclip dans les réponses qu'ils fourni aux requêtes TJS ?

* l'IHM de Géoclip présente les données sous la forme d'une organisation à 2 niveaux :
** une espèce de thème
** pour chaque thème, une liste d'indicateurs disponibles
Comment cette organisatio est-elle extraite des réponses des requêtes TJS ?