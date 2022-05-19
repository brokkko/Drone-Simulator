import React, { Component } from "react";
import "./Controller.css"

class Controller extends Component{

    constructor(props) {
        super(props);
        this.disconnectedColor = 0x00ff00;
        this.connectedColor = 0x4D4D4D;
        this.states = []
        this.states.fill(0);
        this.state = {states: this.states}
    }

    toConnect = () =>{
        this.props.toConnect()
    }

    onPushButton = (id) =>{
        this.props.onPushButton(id-1)
        this.states[id] = (this.states[id] === 0 ? 1 : 0);
        this.setState({states: this.states})
    }

    render() {

        let buttonNum = 6
        let buttons = []

        for(let i = 1; i<buttonNum; i++){
            buttons.push(<input
                style = {{backgroundColor: this.state.states[i] === 0 ? this.disconnectedColor : this.connectedColor}}
                className="button"
                type='button'
                onClick={() => this.onPushButton(i)}
                value={"Drone " + i}/>);
        }

        return(
            <div className="Controller">
                {buttons}
                <input
                    style = {{backgroundColor: this.state.states[0] === 0 ? this.disconnectedColor : this.connectedColor}}
                    className="connectButton"
                    type='button'
                    onClick={this.toConnect}
                    value="CONNECT"/>
            </div>
        )
    }
}

export default Controller