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
        if(this.drones.length === 0){
            this.fillDronesList(coordinates);
            return;
        }

        for(let index in coordinates){
            this.drones[index].position.copy(coordinates[index].pos)
            console.log(coordinates[index].connected)
            this.drones[index].setColor(coordinates[index].connected);
        }

    }
}

export default DronesRenderer

