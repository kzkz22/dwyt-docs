# Adatvédelmi tájékoztató – dwyt / Privacy policy – dwyt

*Hatályos: 2026. október 11. / Effective: 11 October 2026*

## Magyarul

A **dwyt** videók és hangfelvételek átiratát, fordítását és összefoglalóját készíti, felhasználónként külön könyvtárban. Ez a tájékoztató a `dwyt.iodate.date` címen futó példányra vonatkozik; azt egy magánszemély üzemelteti, meghívott felhasználóknak (család, munkatársak, ismerősök).

**Belépés Google-lel.** A Google-belépésből csak a fiók állandó azonosítóját, az e-mail-címet és a nevet kapjuk meg (`openid email profile`). Jelszót nem tárolunk. Más Google-adatot nem kérünk.

**YouTube-feliratkozások (nem kötelező).** Ha a Csatornák oldalon összekapcsolod a YouTube-fiókodat, a központ csak olvasási jogot kér (`youtube.readonly`), és ezzel naponta egyszer kiolvassa, mely csatornákra vagy feliratkozva (a csatornák azonosítóját és nevét). Mást nem olvas, és a fiókodban semmit nem változtat. A Google által adott tartós hozzáférést (refresh token) titkosítva tároljuk; a leválasztáskor töröljük, és a Google-nél is visszavonjuk. A csatornák új videóit a YouTube nyilvános hírcsatornáiból nézzük, belépés nélkül.

**Értesítések (nem kötelező).** Ha a Beállítások oldalon ntfy-t vagy Home Assistantet adsz meg, a kész elemek címét, az összefoglaló első mondatait és a hibaüzeneteket az általad megadott szolgáltatásnak küldjük. Az ehhez megadott tokent titkosítva tároljuk. A nyilvános `ntfy.sh` szerveren az üzenetet bárki olvashatja, aki a téma nevét ismeri; ezért nehezen kitalálható témát javasolunk.

**Mit tárol a központ:** a fiókadatokat (e-mail-cím, név, a belépések ideje), a könyvtárat (a beküldött videók címe és adatai, az átiratok, az összefoglalók), a munkák állapotát, a párosított futtatók adatait, valamint a követett csatornákat, a hozzájuk tartozó szabályokat és a postaláda tartalmát (az új videók címe). Hangot és videót nem tárol.

**Mit nem lát a központ:** a felhasználók AssemblyAI-, OpenRouter- és egyéb kulcsait. Ezek a felhasználó saját futtatóján vannak; a letöltést, az átírást és az összefoglalót a futtató végzi, a felhasználó saját szolgáltatóinál.

**Ki látja az adatokat:** minden felhasználó csak a saját könyvtárát látja; ezt az adatbázis is kikényszeríti. Az üzemeltető (admin) a felületen csak a fiókadatokat és a számokat (elemek, futtatók száma) látja, a könyvtárakat nem. Harmadik félnek nem adjuk át, nem adjuk el, hirdetésre nem használjuk.

**Újrahasznosítás:** ha két felhasználó ugyanazt a nyilvános videót kéri ugyanazokkal a beállításokkal, az eredmény (átirat, összefoglaló) a második felhasználónál is felhasználható, név nélkül. Saját felvétel eredménye csak a feltöltő engedélyével.

**Törlés:** az elemek egyenként törölhetők; a fiók és a könyvtár törlését az üzemeltetőtől lehet kérni (a fióktörlés a felületen később érkezik). A Google-hozzáférés a Google-fiókban is visszavonható: [myaccount.google.com/permissions](https://myaccount.google.com/permissions).

Az alkalmazás a Google-ből kapott adatok használatakor betartja a [Google API Services User Data Policy](https://developers.google.com/terms/api-services-user-data-policy) szabályait, a „Limited Use” követelményekkel együtt.

Kapcsolat: [GitHub-issue](https://github.com/kzkz22/dwyt-docs/issues) ebben a repóban, vagy a meghívót küldő üzemeltető.

## In English

**dwyt** makes transcripts, translations and summaries of videos and recordings, in a separate library for each user. This policy covers the instance at `dwyt.iodate.date`, run by a private person for invited users.

**Google sign-in** gives us only the account's stable ID, e-mail address and name (`openid email profile`). No password is stored; no other Google data is requested.

**YouTube subscriptions (optional).** If you connect your YouTube account on the Channels page, the service asks for read-only access (`youtube.readonly`) and reads, once a day, which channels you subscribe to (channel IDs and names). Nothing else is read and nothing is changed in your account. The long-lived access (refresh token) Google gives is stored encrypted; disconnecting deletes it and revokes it at Google. New videos are taken from YouTube's public channel feeds, without sign-in.

**Notifications (optional).** If you set up ntfy or Home Assistant on the Settings page, the titles of finished items, the first sentences of their summaries and error messages are sent to the service you chose. Its token is stored encrypted. On the public `ntfy.sh` server anyone who knows the topic name can read the messages, so a hard-to-guess topic is suggested.

**Stored centrally:** account data, the library (titles and details of submitted videos, transcripts, summaries), job states, paired runners, and the followed channels with their rules and the inbox (titles of new videos). No audio or video.

**Not seen centrally:** users' API keys (AssemblyAI, OpenRouter, …). They stay on the user's own runner, which does the downloading, transcription and summarising with the user's own providers.

**Access:** each user sees only their own library, enforced by the database too. The operator sees account data and counts, not libraries. Nothing is shared with or sold to third parties or used for advertising.

**Reuse:** when two users request the same public video with the same settings, the result may be reused for the second user, without naming the first. Results of own recordings only with the uploader's permission.

**Deletion:** items can be deleted one by one; account deletion on request (self-service later). Google access can be revoked at [myaccount.google.com/permissions](https://myaccount.google.com/permissions).

The app's use of information received from Google APIs adheres to the [Google API Services User Data Policy](https://developers.google.com/terms/api-services-user-data-policy), including the Limited Use requirements.

Contact: a [GitHub issue](https://github.com/kzkz22/dwyt-docs/issues) in this repository, or the operator who invited you.
