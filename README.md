# Spotify lyttedashboard

Jeg startet dette lille prosjektet på bakgrunn av at jeg ville lære meg `Airflow` for
ETL-prosesser og bygge et dataprodukt ut ifra dataen. I denne omgang ble det et dataprodukt som
viser lyttermønstrene i perioden 2021-2025 med utgangspunkt i to tilgjengelige datakilder:

1. Scrobbling-data fra Last.fm brukeren min, og
2. "Saved Songs/Likte Sanger" spillelisten på Spotify.

## Funksjonalitet

Airflow DAGs for å hente ut, transformere og laste inn data inn i min lokale PostgreSQL
database.

Forsøkte å lage et Unknown Pleasures inspirert plot av lytteaktivitet i løpet av døgnene i
en uke.

Mer som en måte for meg å se hvordan musikksmaken endrer seg fra år til år, og fra måned til
måned.

Lyttefordelingen utover året har funksjon som minner til å se hva som har påvirket lyttingen
for hver måned.

Se hva slags type musikk som overtak blant mine likte sanger, både med tanke på sjanger men
også 'audio artists'.

Artist-diagram med oversikt over hvilke artister som har jobbet med hverandre, tatt ut ifra
mitt eget bibliotek.

## Hva har jeg lært?

- Erfart og undervurdert hvor utfordrende det kan være å jobbe med forskjellige men høyst
  relaterte datakilder.
- Bruke `uv` for å lage lokale packages for å lage scripts for gjenbruk i flere deler av koden.
- Airflow for orkestrering av ETL-prosesser.
- Oppsett av Airflow med Docker på lokal maskin.
- Bruk av Pythons `logging`-bibliotek.

## Utfordringer jeg møtte på

- Finne ut hva som var galt med DAG-scriptene når de ikke blir gjenkjent i Airflow.

## Veien videre:

Vel, jeg skulle gjerne likt å ha tilgang til all lytterdataen min hos Spotify som hadde tillat
å kartlegge lytterdataen slik jeg først hadde tenkt det til. Da blir det å spørre om
lytterdataen sin tidlig 2026 slik at 2025 som helhet blir tatt hensyn til. Dette åpner også opp
for at det blir lettere å hente ut audio features fra en lignende API til Spotify sin.

Analysen kan utvides til å ta fatt på albumene jeg har lagret i biblioteket eller spillelister
jeg har tilgjengelig.

Og så klart kan man drive å refactore store deler av koden også...

Sist men ikke minst: å deploye dashboardet!

## Hva hadde jeg egentlig planlagt?

Før jeg naivt hoppet inn i prosjektet var idéen å lage en daglig, ukentlig og månedlig
oppsummeringer av lyttermønsteret mitt som oppdaterte hver dag ut ifra Spotify sin API. Planen
ble kjapt avsporet fra det faktum at API-endepunktet ([Get Recent
Tracks](https://developer.spotify.com/documentation/web-api/reference/get-recently-played)) kun
er i stand til å hente de 50 siste sangene spilt. I tillegg hadde jeg også planlagt å gjøre en
"audio feature"-analyse av sanger på tvers av flere spillelister tilgjengelig på brukeren min,
men Spotify hadde så klart [skrotet bort det API-endepunktet](https://developer.spotify.com/documentation/web-api/reference/get-several-audio-features)
🙃.

Til tross for dette ville jeg fremdeles bygge noe ut ifra dataen jeg besitter.

<!-- ## FAQ -->
<!---->
<!-- Q: Hvorfor ikke bruke BI-løsninger som PowerBI o.l. for dashboardet? -->
<!---->
<!-- A: Jobber med en Mac så har ikke tilgang til PowerBI uten en virtual machine. Prøvde meg på -->
<!-- Metabase og Apache Superset men skjønte raskt at en BI-løsning ikke var passelig. Derfor falt -->
<!-- valget på Streamlit for mer finurlig kontroll av dashboardets utseende. -->
