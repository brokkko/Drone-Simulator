import React, { Component } from "react";
import Drone from "./Drone.js"

class DronesRenderer{
    constructor(scene) {
        this.drones = []
        this.scene = scene
    }

    fillDronesList(positions){
        for (let index in positions){
            this.drones.push(new Drone(positions[index].pos));
            this.drones[index].setColor(positions[index].connected);
            this.scene.add(this.drones[index])
        }
    }


    updatePositions(coordinates){

        for (let i of coordinates){
            i.pos.multiplyScalar(1/10)
        }

        if(this.drones.length === 0){ // if no drones created yet
            this.fillDronesList(coordinates);
            return;
        }

        for(let index in coordinates){ // update
            this.drones[index].position.copy(coordinates[index].pos)
            this.drones[index].setColor(coordinates[index].connected);
        }

    }
}

export default DronesRenderer

