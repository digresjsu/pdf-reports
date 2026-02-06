import { Component, useState } from "@odoo/owl";

export class Playground extends Component {
    static template = "digresjsu.Counter";

    setup() {
        this.state = useState({ count : 0 });
    }

    increment() {
        this.state.count++;
    }
}
