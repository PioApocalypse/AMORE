prov_code = {
    "Agrigento": "Ag",
    "Alessandria": "Al",
    "Ancona": "An",
    "Aosta": "Ao",
    "Arezzo": "Ar",
    "Ascoli Piceno": "Ap",
    "Asti": "At",
    "Avellino": "Av",
    "Bari": "Ba",
    "Barletta-Andria-Trani": "Bt",
    "Belluno": "Bl",
    "Benevento": "Bn",
    "Bergamo": "Bg",
    "Biella": "Bi",
    "Bologna": "Bo",
    "Bolzano": "Bz",
    "Brescia": "Bs",
    "Brindisi": "Br",
    "Cagliari": "Ca",
    "Caltanissetta": "Cl",
    "Campobasso": "Cb",
    "Caserta": "Ce",
    "Catania": "Ct",
    "Catanzaro": "Cz",
    "Chieti": "Ch",
    "Como": "Co",
    "Cosenza": "Cs",
    "Cremona": "Cr",
    "Crotone": "Kr",
    "Cuneo": "Cn",
    "Enna": "En",
    "Fermo": "Fm",
    "Ferrara": "Fe",
    "Firenze": "Fi",
    "Foggia": "Fg",
    "Forlì-Cesena": "Fc",
    "Frosinone": "Fr",
    "Genova": "Ge",
    "Gorizia": "Go",
    "Grosseto": "Gr",
    "Imperia": "Im",
    "Isernia": "Is",
    "LAquila": "Aq",
    "La Spezia": "Sp",
    "Latina": "Lt",
    "Lecce": "Le",
    "Lecco": "Lc",
    "Livorno": "Li",
    "Lodi": "Lo",
    "Lucca": "Lu",
    "Macerata": "Mc",
    "Mantova": "Mn",
    "Massa-Carrara": "Ms",
    "Matera": "Mt",
    "Messina": "Me",
    "Milano": "Mi",
    "Modena": "Mo",
    "Monza e della Brianza": "Mb",
    "Napoli": "Na",
    "Novara": "No",
    "Nuoro": "Nu",
    "Oristano": "Or",
    "Padova": "Pd",
    "Palermo": "Pa",
    "Parma": "Pr",
    "Pavia": "Pv",
    "Perugia": "Pg",
    "Pesaro e Urbino": "Pu",
    "Pescara": "Pe",
    "Piacenza": "Pc",
    "Pisa": "Pi",
    "Pistoia": "Pt",
    "Pordenone": "Pn",
    "Potenza": "Pz",
    "Prato": "Po",
    "Ragusa": "Rg",
    "Ravenna": "Ra",
    "Reggio Calabria": "Rc",
    "Reggio Emilia": "Re",
    "Rieti": "Ri",
    "Rimini": "Rn",
    "Roma": "Rm",
    "Rovigo": "Ro",
    "Salerno": "Sa",
    "Sassari": "Ss",
    "Savona": "Sv",
    "Siena": "Si",
    "Siracusa": "Sr",
    "Sondrio": "So",
    "Taranto": "Ta",
    "Teramo": "Te",
    "Terni": "Tr",
    "Torino": "To",
    "Trapani": "Tp",
    "Trento": "Tn",
    "Treviso": "Tv",
    "Trieste": "Ts",
    "Udine": "Ud",
    "Varese": "Va",
    "Venezia": "Ve",
    "Verbano-Cusio-Ossola": "Vb",
    "Vercelli": "Vc",
    "Verona": "Vr",
    "Vibo Valentia": "Vv",
    "Vicenza": "Vi",
    "Viterbo": "Vt"
}

def location_to_code(location_name):
    return prov_code.get(location_name, "Xx")