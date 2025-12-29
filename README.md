Prosjektet tar utgangspunkt i to datakilder:

1. Scrobbling data fra min Last.fm
2. "Saved Songs"/"Likte Sanger" spillelisten på Spotify

## Hva hadde jeg egentlig planlagt?

Før jeg naivt hoppen i prosjektet ønsket var idéen å lage en daglig, ukentlig og månedlige
oppsummeringer av lyttermønsteret mitt som oppdaterte hver dag. Planen ble kjapt sporet av det
faktum at Spotify sin API ([Get Recent
Tracks](https://developer.spotify.com/documentation/web-api/reference/get-recently-played)) kun
er i stand til å hente de 50 siste sangene spilt. I tillegg hadde jeg også planlagt å gjøre en
"audio feature"-analyse av sanger på tvers av alle spillelister tilgjengelig på brukeren min,
men Spotify hadde så klart skrotet bort det
[API-endpointet](https://developer.spotify.com/documentation/web-api/reference/get-several-audio-features)
også 🙃.

Til tross for dette ville jeg fremdeles bygge noe ut ifra dataen jeg besitter.

## FAQ

Q: Hvorfor ikke bruke BI-løsninger som PowerBI o.l. for dashboardet? A: Jobber med en Mac så
har ikke tilgang til PowerBI. Prøvde meg på Metabase og Apache Superset som ikke helt matchet
hva jeg trengte.

## Hva har jeg lært?

- Skrive packages, utils scripts som kan bli brukt hvor enn man er i kodebasen uten å måtte
  bruke `sys` og `pathlib.Path`
- Hvordan drive med packaging ved bruk av `uv` for å ha scripts for gjenbruk.
- Airflow for orkestrering av ETL-prosesser.
- Bruke Pythons `logging`-bibliotek.
- Jobbe med forskjellige, men relaterte datakilder er komplisert og frustrerende.
- Spotify har skrotet sin mest interessante API-endpoint, som sto til grunn for prosjektet.
- Oppsett av Airflow med Docker på lokal maskin

## Utfordringer jeg møtte på

- Finne ut hva som var galt med DAG-scriptene når de ikke blir gjenkjent i Airflow.
-

## Veien videre:

- Vel, jeg skulle gjerne likt å ha tilgang til all lytterdataen gjennom Spotify, ikke last.fm,
  for å drive mer "substansiell" analyse av lyttemønstrene mine. Dette er mulig å ta opp i tidlig
  2026 en gang for å gjøre analysen mer komplett.
