import {Vector3} from "three"

// 10.4 40 75.45879|47.45 78 100.0|...|78.7 56 789.2
function parseData(data){
    let positions = []
    for (let coordStr of data.split('|')){
        let coord = coordStr.split(' ')
        coord.forEach(parseFloat)
        positions.push(new Vector3(coord[0],coord[1],coord[2]))
    }
    return positions
}

export default parseData