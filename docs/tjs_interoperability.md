# TJS Interoperability

OneTjs implements the international OGC standard called Table Joining Service 1.0
(see http://www.opengeospatial.org/standards/tjs). It has been designed to provide data to TJS client applications.

For the french market the main TJS solution is Géoclip.


## Géoclip

### Géoclip O3

Géoclip acts as a TJS server and a TJS client.  
The TJS specification is not yet implemented in Géoclip Air. You need to use the O3 version of Géoclip in order to 
connect to TJS servers. 

The way Géoclip O3 implements TJS is not perfect. Some specificities have been introduced in OneTjs in order to a 
good level of interoperability with Géoclip Air. This is the reason why we have created a specialised TJS end-point 
for Géoclip in addition to a more generic one.

For example, for the "divers" service OneTjs provides 2 TJS:
* http://localhost:5000/tjs/divers
* http://localhost:5000/tjs_geoclip/divers

The second one provides TJS responses conformant with the expectations of Géoclip O3. It will probably not be 
maintained in the long term. Géoclip Air will probably be able to consume the first one. Most TJS clients should use 
the first one (much cleaner/compact XML syntax).


Géoclip O3 is quite surprised when finding orphan frameworks (framework not used by any dataset). Make sure that all 
the frameworks you have configured in OneTjs are used by at least one dataset.


### Géoclip Air

Géoclip O3 is not yet a TJS client.  
Implementation of TJS in this version would hopefully occur by the end of 2018.


## Any other robust TJS client application?
