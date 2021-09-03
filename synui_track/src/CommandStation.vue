<template>
    <div id="viewport">
        <!-- <div id="control-bar" class="container">
            <span id="checkbox">
                <input
                    id="checkbox-element"
                    type="checkbox"
                    v-model="draggable"
                />
                <i class="bi bi-arrows-move"></i>
            </span>
            <span id="checkbox">
                <input
                    id="checkbox-element"
                    type="checkbox"
                    v-model="resizable"
                />
                <i class="bi bi-aspect-ratio"></i>
            </span>
            <span id="checkbox">
                <input
                    id="checkbox-element"
                    type="checkbox"
                    v-model="responsive"
                />
                <i class="bi bi-grid-1x2"></i>
            </span>
        </div> -->
        <div id="command-station">
            <grid-layout
                :layout.sync="layout"
                :col-num="18"
                :row-height="35"
                :is-draggable="draggable"
                :is-resizable="resizable"
                :responsive="responsive"
                :vertical-compact="true"
                :use-css-transforms="true"
            >
                <grid-item
                    v-for="item in layout"
                    :x="item.x"
                    :y="item.y"
                    :w="item.w"
                    :h="item.h"
                    :i="item.i"
                    :key="item.i"
                >
                    <iframe
                        :src="retrieveUrl(ranks[item.i])"
                        id="window"
                        allowfullscreen
                        frameborder="0"
                        wmode="transparent"
                    >
                        Your browser doesn't support iframes
                    </iframe>
                </grid-item>
            </grid-layout>
        </div>
    </div>
</template>


<script lang="ts">
import { GridLayout, GridItem } from "vue-grid-layout";

// Declare custom typings
type Window = {
    x: number;
    y: number;
    w: number;
    h: number;
    i: number;
};
type Layout = Array<Window>;

export default {
    name: "CommandStation",
    props: ["args"], // Arguments that are passed to the plugin in Python are accessible in props `args`. Here, we access the "name" arg.
    components: {
        GridLayout,
        GridItem,
    },
    data(this: any) {
        return {
            ranks: this.computeRanks(),
            layout: this.computeLayout(),
            draggable: true,
            resizable: true,
            responsive: true,
            index: 0,
        };
    },
    methods: {
        computeRanks(this: any): Array<string> {
            const PRIORITY = ["MQ", "Logs", "MLOps", "Catalogue", "Meter"];
            const components = Object.keys(this.args);
            const ranks = PRIORITY.filter((value) =>
                components.includes(value)
            );
            return ranks;
        },

        computeLayout() {
            const oneComponent = [{ x: 0, y: 0, w: 12, h: 18, i: 0 }];
            const twoComponent = [
                { x: 0, y: 0, w: 6, h: 18, i: 0 },
                { x: 6, y: 0, w: 6, h: 18, i: 1 },
            ];
            const threeComponent = [
                { x: 0, y: 0, w: 12, h: 9, i: 0 },
                { x: 0, y: 9, w: 6, h: 9, i: 1 },
                { x: 6, y: 9, w: 6, h: 9, i: 2 },
            ];
            const fourComponent = [
                { x: 0, y: 0, w: 6, h: 9, i: 0 },
                { x: 0, y: 9, w: 6, h: 9, i: 1 },
                { x: 6, y: 0, w: 6, h: 9, i: 2 },
                { x: 6, y: 9, w: 6, h: 9, i: 3 },
            ];
            const fiveComponent = [
                { x: 0, y: 0, w: 6, h: 9, i: 0 },
                { x: 6, y: 0, w: 6, h: 9, i: 1 },
                { x: 0, y: 9, w: 4, h: 9, i: 2 },
                { x: 4, y: 9, w: 4, h: 9, i: 3 },
                { x: 8, y: 9, w: 4, h: 9, i: 4 },
            ];

            const COUNTMAP: { [componentCount: number]: Layout | [] } = {};
            COUNTMAP[0] = [];
            COUNTMAP[1] = oneComponent;
            COUNTMAP[2] = twoComponent;
            COUNTMAP[3] = threeComponent;
            COUNTMAP[4] = fourComponent;
            COUNTMAP[5] = fiveComponent;

            const noOfComponents = this.computeRanks().length;

            return COUNTMAP[noOfComponents];
        },

        retrieveUrl(this: any, name: string): string {
            const url = this.args[name];
            return url;
        },
    },
};
</script>


<style scoped>
#viewport {
    width: 100%; 
    height: auto;
}

/* #control-bar {
    display: block;
    text-align: right;
}

#checkbox {
    background: #f5f5f5;
    display: inline-block;
    padding: 10px 10px;
    border-radius: 2px;
    position: relative;
    cursor: pointer;
}

#checkbox-element {
    display: block;
    position: absolute;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    z-index: 99999;
    opacity: 0;
}

#checkbox > input[type="checkbox"] + i {
    color: black;
}

#checkbox > input[type="checkbox"]:checked + i {
    color: #da7f4d;
} */

.vue-grid-layout {
    background: #f5f5f5;
}
.vue-grid-item:not(.vue-grid-placeholder) {
    background: #ffffff;
    border: 1px solid black;
}
.vue-grid-item .resizing {
    opacity: 0.9;
}
.vue-grid-item .static {
    background: #cce;
}
.vue-grid-item .text {
    font-size: 24px;
    text-align: center;
    position: absolute;
    top: 0;
    bottom: 0;
    left: 0;
    right: 0;
    margin: auto;
    height: 100%;
    width: 100%;
}
.vue-grid-item .no-drag {
    height: 100%;
    width: 100%;
}
.vue-grid-item .minMax {
    font-size: 12px;
}
.vue-grid-item .add {
    cursor: pointer;
}
.vue-draggable-handle {
    position: absolute;
    width: 20px;
    height: 20px;
    top: 0;
    left: 0;
    /* background: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='10' height='10'><circle cx='5' cy='5' r='5' fill='#999999'/></svg>")
        no-repeat; */
    background-position: bottom right;
    padding: 0 8px 8px 0;
    background-repeat: no-repeat;
    background-origin: content-box;
    box-sizing: border-box;
    cursor: pointer;
}
.layoutJSON {
    background: #ddd;
    border: 1px solid black;
    margin-top: 10px;
    padding: 10px;
}
.columns {
    -moz-columns: 120px;
    -webkit-columns: 120px;
    columns: 120px;
}

#window {
    width: 100%;
    height: 100%;
    position: relative;
}
</style>