# openzone-webovky
Web napsaný v pythonu za pomoci jinji a mongodb

Pro spuštění budete potřebovat mongo a *config.py* soubor, který vložíte do projektu. Ten bude obsahovat následující: \

**secret = b'SECRET KEY (náhodná čísla ke cookies a formu)'**\
**connection_string = "MONGO DB CONNECTION STRING"**\
**form_id = "Id dokumentu s hlasy (v db v "openzone.form")"**\
**names_id = "Id dokumentu s s hlasujícími (v db opět v "openzone.form")"**


![mongo1](https://media.discordapp.net/attachments/782281045236121610/922129471346184262/unknown.png "Pohled na db")
![mongo2](https://media.discordapp.net/attachments/782281045236121610/922129480850485338/unknown.png "Oba dokumenty v openzone.form")
