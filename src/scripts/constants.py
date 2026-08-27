PRIMARY_POS_ORDER = ['GK', 'DF', 'MF', 'FW']

# raw source data ships these already divided by 90s, rather than as true counts.
# shared between the preprocessing script (multiplies back to counts) and the
# notebook's own per-90 step (divides back down), so the two can't drift apart.
PER90_COUNT_COLUMNS = [
    'Goals', 'Shots', 'SoT', 'ShoFK', 'ShoPK', 'PKatt', 'PasTotCmp', 'PasTotAtt',
    'PasTotDist', 'PasTotPrgDist', 'PasShoCmp', 'PasShoAtt', 'PasMedCmp', 'PasMedAtt',
    'PasLonCmp', 'PasLonAtt', 'Assists', 'PasAss', 'Pas3rd', 'PPA', 'CrsPA',
    'PasProg', 'PasAtt', 'PasLive', 'PasDead', 'PasFK', 'TB', 'PasPress', 'Sw',
    'PasCrs', 'CK', 'CkIn', 'CkOut', 'CkStr', 'PasGround', 'PasLow', 'PasHigh',
    'PaswLeft', 'PaswRight', 'PaswHead', 'TI', 'PaswOther', 'PasCmp', 'PasOff',
    'PasOut', 'PasInt', 'PasBlocks', 'SCA', 'ScaPassLive', 'ScaPassDead', 'ScaDrib',
    'ScaSh', 'ScaFld', 'ScaDef', 'GCA', 'GcaPassLive', 'GcaPassDead', 'GcaDrib',
    'GcaSh', 'GcaFld', 'GcaDef', 'Tkl', 'TklWon', 'TklDef3rd', 'TklMid3rd',
    'TklAtt3rd', 'TklDri', 'TklDriAtt', 'TklDriPast', 'Press', 'PresSucc',
    'PresDef3rd', 'PresMid3rd', 'PresAtt3rd', 'Blocks', 'BlkSh', 'BlkShSv',
    'BlkPass', 'Int', 'Tkl+Int', 'Clr', 'Err', 'Touches', 'TouDefPen', 'TouDef3rd',
    'TouMid3rd', 'TouAtt3rd', 'TouAttPen', 'TouLive', 'DriSucc', 'DriAtt',
    'DriPast', 'DriMegs', 'Carries', 'CarTotDist', 'CarPrgDist', 'CarProg',
    'Car3rd', 'CPA', 'CarMis', 'CarDis', 'RecTarg', 'Rec', 'RecProg', 'CrdY',
    'CrdR', '2CrdY', 'Fls', 'Fld', 'Off', 'Crs', 'TklW', 'PKwon', 'PKcon',
    'OG', 'Recov', 'AerWon', 'AerLost'
]
