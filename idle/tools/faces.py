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
    'velia': (0.235, 0.19, 0.22), 'knochenkoloss': (0.525, 0.15, 0.14), 'malhar': (0.49, 0.14, 0.17),
    'leerenbrut': (0.42, 0.52, 0.3), 'tentakelmeister': (0.26, 0.4, 0.45), 'abgrundwaechter': (0.415, 0.14, 0.15),
    # raid and world bosses
    'magmaul': (0.15, 0.26, 0.28), 'glutweberin': (0.34, 0.39, 0.25), 'aschenfaust': (0.39, 0.16, 0.2),
    'ignis': (0.17, 0.13, 0.2), 'varn': (0.53, 0.13, 0.18), 'bleiche_dame': (0.45, 0.13, 0.17),
    'nivara': (0.22, 0.38, 0.22), 'nebelkoenig': (0.53, 0.15, 0.19), 'sternenfresser': (0.15, 0.4, 0.3),
    'zwillingsaugen': (0.33, 0.48, 0.5), 'xaroth': (0.11, 0.24, 0.22), 'nhalzor': (0.415, 0.39, 0.38),
    'azurschwinge': (0.115, 0.27, 0.22), 'grollhuf': (0.14, 0.3, 0.22), 'verderbte_eiche': (0.17, 0.29, 0.25),
    'eiche': (0.27, 0.31, 0.22),
    # companions, painted
    'comp_tank': (0.475, 0.125, 0.15), 'comp_zauberin': (0.445, 0.21, 0.13), 'comp_heiler': (0.5, 0.085, 0.11),
    'comp_schuetze': (0.445, 0.11, 0.11),
    # heroes of the other peoples
    'hero_krieger_zwerg': (0.6, 0.19, 0.22), 'hero_magier_zwerg': (0.59, 0.17, 0.2), 'hero_jaeger_zwerg': (0.24, 0.18, 0.22),
    'hero_priester_zwerg': (0.515, 0.13, 0.18),
    'hero_krieger_elf': (0.37, 0.1, 0.09), 'hero_magier_elf': (0.37, 0.1, 0.09), 'hero_jaeger_elf': (0.45, 0.1, 0.1),
    'hero_priester_elf': (0.52, 0.075, 0.09),
    'hero_krieger_ork': (0.45, 0.1, 0.13), 'hero_magier_ork': (0.365, 0.2, 0.15), 'hero_jaeger_ork': (0.46, 0.18, 0.17),
    'hero_priester_ork': (0.53, 0.2, 0.17),
    'hero_krieger_halbling': (0.49, 0.19, 0.2), 'hero_magier_halbling': (0.47, 0.24, 0.2), 'hero_jaeger_halbling': (0.53, 0.18, 0.22),
    'hero_priester_halbling': (0.53, 0.18, 0.2),
    'hero_krieger_untot': (0.45, 0.12, 0.12), 'hero_magier_untot': (0.59, 0.135, 0.12), 'hero_jaeger_untot': (0.54, 0.13, 0.11),
    'hero_priester_untot': (0.43, 0.15, 0.12),
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
        elif n.count('_') == 2 and n.startswith('hero_') and ('hero_' + n.split('_')[1]) in FACES:
            out[n] = list(FACES['hero_' + n.split('_')[1]])
        elif n.startswith('npc_'):
            out[n] = [0.5, 0.1, 0.11]
        elif not n.startswith('fx_'):
            out[n] = [0.5, 0.25, 0.3]
    return out
