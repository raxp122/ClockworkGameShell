# ClockworkGameShell

Warehouse personale per il **ClockworkPi GameShell** (schermo 320×240): giochi e
tool installabili direttamente dal menu **Warehouse** della console. La struttura
è la stessa del warehouse ufficiale
[clockworkpi/warehouse](https://github.com/clockworkpi/warehouse).

## Aggiungere il warehouse al GameShell

1. Sul GameShell apri **Warehouse** (serve il Wi-Fi attivo).
2. Scegli **Add new warehouse...**.
3. Scrivi `github.com/raxp122/ClockworkGameShell` e conferma.
4. Apri la nuova voce, scegli un gioco e premi **A** per scaricarlo. Quando il
   download è finito, premi **A** di nuovo per avviarlo.

> ⚠️ Il launcher legge **sempre il branch `master`**: l'URL `master/index.json`
> è scritto nel codice del launcher. Le modifiche entrano in `main` tramite
> PR, e subito dopo `main` viene unito in `master`, che è quello che il
> GameShell scarica.

## Contenuto

| Categoria | Titolo    | Tipo     | Descrizione |
|-----------|-----------|----------|-------------|
| Tools     | KeyTester | launcher | Mostra tutti i tasti premuti, compresa la Lightkey sul retro. Per uscire tieni premuto MENU. |

## Struttura

```
index.json                      ← elenco delle categorie (generato)
<Categoria>/
  index.json                    ← elenco dei giochi (generato)
  <Titolo>/
    .game                       ← tipo: launcher | pico8 | tic80
    src/                        ← sorgenti (solo tipo launcher)
      <Titolo>.sh               ← script di avvio, eseguito dentro la cartella del gioco
    file/<Titolo>.tar.gz        ← pacchetto (generato da src/)
    shots/<Titolo>.png          ← anteprima 320×240 mostrata nel Warehouse
```

- **launcher**: qualsiasi programma avviato da `<Titolo>.sh`, per esempio
  `python main.py` (pygame), `love gioco.love` (LÖVE) o un binario ARM.
- **pico8**: metti la cartuccia `*.p8.png` in `file/`, senza `src/`.
- **tic80**: metti la cartuccia `*.tic` in `file/`, senza `src/`.

Nei nomi di categorie e giochi evita apostrofi, virgolette e caratteri come
`$ ; & |`: il launcher li usa per costruire comandi SQL e shell.

## Aggiungere un gioco

```bash
mkdir -p Games/MioGioco/src Games/MioGioco/shots
echo launcher > Games/MioGioco/.game
# metti i sorgenti in src/, con src/MioGioco.sh come script di avvio
python3 scripts/build.py
```

`scripts/build.py` crea i `.tar.gz` e rigenera tutti gli `index.json`. Va
lanciato prima di ogni commit.

## Note tecniche (Clockwork OS stock)

- Python di sistema: **Python 2** con pygame 1.9. Il codice deve restare
  compatibile con Python 2 e 3.
- Mappa dei tasti vista da pygame (verificata con KeyTester):

  | Tasto                  | Invia                 | Note |
  |------------------------|-----------------------|------|
  | Frecce                 | `Up Down Left Right`  | |
  | A / B / X / Y          | `K` / `J` / `I` / `U` | layout SNES; con il layout Xbox A/B e X/Y si scambiano |
  | MENU / SELECT / START  | `Esc` / `Space` / `Enter` | |
  | SHIFT                  | niente                | modificatore hardware |
  | Lightkey 1 (sinistra)  | `H`                   | uguale a SHIFT+B |
  | Lightkey 2             | `Y`                   | uguale a SHIFT+Y |
  | Lightkey 3 (centro)    | niente                | è un secondo SHIFT |
  | Lightkey 4             | `O`                   | uguale a SHIFT+X |
  | Lightkey 5 (destra)    | `L`                   | uguale a SHIFT+A |
  | SHIFT+START / SELECT / MENU | `KP+` / `KP-` / `Backspace` | |

  Un gioco quindi non distingue una Lightkey dalla combinazione SHIFT
  equivalente, e non può leggere SHIFT o la Lightkey centrale da soli.
  KeyTester salva i tasti premuti in `keylog.txt` nella sua cartella.
- I giochi installati finiscono in `~/aria2download/raxp122/ClockworkGameShell/master/…`.
