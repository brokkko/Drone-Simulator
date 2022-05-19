from src.Vector import Vector

# 6 drones flying at each other(3X3)
positionsList1 = [(59.86805732560133, 30.56717405661705), (59.86805732560371, 30.567188808769522),
                  (59.868057325604035, 30.567201549263782), (59.867993559987376, 30.56718404313254),
                  (59.867992213527096, 30.56719879526668), (59.86799288676702, 30.567170632097273)]
targets1 = [Vector(-3, -10, 25), Vector(0, -10, 25), Vector(3, -10, 25),
            Vector(-3, 10, 25), Vector(0, 10, 25), Vector(3, 10, 25)]

# 2 drones flying at each other
positionsList2 = [(59.86805732560133, 30.56717405661705), (59.867993559987376, 30.56718404313254)]
targets2 = [Vector(-3, -10, 25), Vector(-3, 10, 25)]

# 4 drones flying in one direction
positionsList3 = [(59.868012717193984, 30.567235680640323), (59.8680117073538, 30.5672497622265),
                  (59.86801170735036, 30.567263173261424), (59.868011707346014, 30.56727658429701)]
targets3 = [Vector(60, 0, 25), Vector(61, 0, 25), Vector(62, 0, 25), Vector(63, 0, 25)]

# 4 drones flying from different sides and intersect at one point
positionsList4 = [(59.94635532180626, 30.817165711747744), (59.94635389728687, 30.817721419704696),
                  (59.94610646277668, 30.817727107896264), (59.946110261889224, 30.817161921032508)]
targets4 = [Vector(31.37696495, -27.72570174, 25),
            Vector(-0.21186666, -27.30256879, 25),
            Vector(1.16614274e-10, -4.74592809e-10, 25),
            Vector(31.05881508, -0.15857792, 25)]


def getTestData(testNumber) -> (list, list):
    if testNumber == 1:
        return positionsList1, targets1
    elif testNumber == 2:
        return positionsList2, targets2
    elif testNumber == 3:
        return positionsList3, targets3
    elif testNumber == 4:
        return positionsList4, targets4
