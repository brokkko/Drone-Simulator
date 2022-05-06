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
        this.props.onPushButton(id)
        this.states[id] = (this.states[id] === 0 ? 1 : 0);
        this.setState({states: this.states})
        console.log(this.states[id])
    }

    render() {
        return(
            <div>
                <input type='button' onClick={this.toConnect} value="CONNECT"/>
            </div>
        )
    }
}

export default Controller