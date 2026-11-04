"""Where each sprite's face is, for round portraits: (x, y, size) as fractions of the sprite as stored in the
atlas (heroes face right, monsters face left). x and y are the centre of the head, size is the head's height
as a share of the sprite's height. Measured by eye on gridded contact sheets; check with tools/faces_sheet.py.
"""

FACES = {
    # heroes (companions and arena rivals derive from these)
    'hero_krieger': (0.607, 0.13, 0.11), 'hero_magier': (0.617, 0.14, 0.11),
    'hero_jaeger': (0.456, 0.105, 0.11), 'hero_priester': (0.53, 0.07, 0.1),
    # normal monsters
    'waldwolf': (0.089, 0.3, 0.3), 'kobold': (0.30, 0.30, 0.24), 'waldspinne': (0.30, 0.50, 0.30),
    'moorschleim': (0.32, 0.45, 0.40), 'sumpfkriecher': (0.40, 0.27, 0.24), 'krokilisk': (0.179, 0.5, 0.34),
    'hyaene': (0.1, 0.327, 0.3), 'oger': (0.36, 0.15, 0.18), 'staubelementar': (0.32, 0.17, 0.20),
    'skorpid': (0.3, 0.62, 0.3), 'mumie': (0.25, 0.16, 0.18), 'sandwurm': (0.28, 0.33, 0.34),
    'yeti': (0.3, 0.255, 0.25), 'frostwolf': (0.12, 0.32, 0.30), 'eiselementar': (0.52, 0.20, 0.20),
    'ghul': (0.32, 0.15, 0.17), 'skelett': (0.48, 0.08, 0.14), 'banshee': (0.314, 0.208, 0.22),
    'feuerelementar': (0.266, 0.18, 0.22), 'lavahund': (0.22, 0.35, 0.30), 'wichtel': (0.35, 0.25, 0.25),
    'leerwandler': (0.333, 0.223, 0.25), 'tentakelgrauen': (0.329, 0.344, 0.4), 'sternenbestie': (0.17, 0.30, 0.30),
    # elites
    'graufang': (0.13, 0.32, 0.32), 'schlammbrocken': (0.18, 0.42, 0.40), 'brug': (0.55, 0.20, 0.17),
    'ankhu': (0.55, 0.11, 0.12), 'eisklaue': (0.33, 0.22, 0.24), 'knochenwaechter': (0.55, 0.14, 0.16),
    'magmagolem': (0.511, 0.121, 0.18), 'augenlose_wache': (0.492, 0.177, 0.15),
    # zone bosses
    'kragg': (0.33, 0.25, 0.30), 'morva': (0.45, 0.33, 0.2), 'gromm': (0.50, 0.20, 0.18), 'khet': (0.45, 0.18, 0.20),
    'glaciara': (0.24, 0.4, 0.3), 'mordrek': (0.45, 0.22, 0.20), 'ignaroth': (0.182, 0.177, 0.25), 'umbrax': (0.12, 0.32, 0.30),
    # dungeon bosses
    'schnarr': (0.46, 0.30, 0.22), 'hoehlenspinne': (0.35, 0.5, 0.28), 'erzkoloss': (0.374, 0.234, 0.18),
    'sporenmutter': (0.20, 0.32, 0.40), 'krokilisk_alpha': (0.14, 0.48, 0.34), 'ulgra': (0.55, 0.25, 0.20),
    'skarabaeus': (0.30, 0.42, 0.30), 'nefra': (0.47, 0.13, 0.17), 'steinwaechter': (0.52, 0.15, 0.20),
    'yeti_boss': (0.45, 0.25, 0.25), 'halvar': (0.50, 0.16, 0.20), 'kryoskelett': (0.47, 0.15, 0.18),
    'velia': (0.35, 0.25, 0.25), 'knochenkoloss': (0.50, 0.15, 0.20), 'malhar': (0.48, 0.15, 0.18),
    'leerenbrut': (0.22, 0.58, 0.25), 'tentakelmeister': (0.42, 0.40, 0.35), 'abgrundwaechter': (0.42, 0.13, 0.15),
    # raid and world bosses
    'magmaul': (0.239, 0.477, 0.25), 'glutweberin': (0.18, 0.55, 0.30), 'aschenfaust': (0.40, 0.14, 0.20),
    'ignis': (0.42, 0.25, 0.30), 'varn': (0.45, 0.15, 0.20), 'bleiche_dame': (0.299, 0.24, 0.26),
    'nivara': (0.15, 0.30, 0.20), 'nebelkoenig': (0.50, 0.15, 0.20), 'sternenfresser': (0.219, 0.457, 0.25),
    'zwillingsaugen': (0.45, 0.40, 0.35), 'xaroth': (0.12, 0.32, 0.20), 'nhalzor': (0.42, 0.40, 0.35),
    'azurschwinge': (0.14, 0.3, 0.2), 'grollhuf': (0.42, 0.12, 0.18), 'verderbte_eiche': (0.383, 0.335, 0.25),
    'eiche': (0.34, 0.3, 0.25),
}


def table(names, derived):
    """Face entries for every sprite name: measured, derived (companions, rivals) or a generic guess."""
    out = {}
    for n in names:
        if n in FACES:
            out[n] = list(FACES[n])
        elif n.startswith('comp_') and derived.get(n) in FACES:
            out[n] = list(FACES[derived[n]])
        elif n.startswith('rival_') and ('hero_' + n[6:]) in FACES:
            x, y, s = FACES['hero_' + n[6:]]
            out[n] = [round(1 - x, 3), y, s]
        elif n.startswith('npc_'):
            out[n] = [0.5, 0.1, 0.11]
        elif not n.startswith('fx_'):
            out[n] = [0.5, 0.25, 0.3]
    return out
