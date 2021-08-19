<template>
    <div style="width: 100%; height: auto">
        <!-- <span> Hello, {{ args }}! </span>
        <a href="mq.url"
            ><button>{{ mq.url }}</button></a
        > -->
        <!-- <div class="container">
            <input type="checkbox" v-model="draggable" />
            <i class="bi bi-arrows-move"></i>
            <input type="checkbox" v-model="resizable" /><i
                class="bi bi-aspect-ratio"
            ></i>
            <input type="checkbox" v-model="responsive" /><i
                class="bi bi-grid-1x2"
            ></i>
        </div> -->
        <div style="width: 100%; height: 100%">
            <grid-layout
                :layout.sync="layout"
                :col-num="12"
                :row-height="35"
                :is-draggable="draggable"
                :is-resizable="resizable"
                :responsive="responsive"
                :vertical-compact="true"
                :use-css-transforms="true"
            >
                <grid-item
                    v-for="item in layout"
                    :static="item.static"
                    :x="item.x"
                    :y="item.y"
                    :w="item.w"
                    :h="item.h"
                    :i="item.i"
                    :key="item.i"
                >
                    <span class="text">{{ item.i }}</span>
                    <iframe
                        src="http://127.0.0.1:9000"
                        id="mq"
                        allowfullscreen
                        frameborder="0"
                        wmode="transparent"
                    >
                        Your browser doesn't support iframes
                    </iframe>
                    <!-- <grid-item :x=0 :y=0 :w=4 :h=18 :i=0 :key="MQ">
                    <iframe
                        src="http://localhost:15672"
                        id="mq"
                        allowfullscreen
                        frameborder="0"
                        wmode="transparent"
                    >
                        Your browser doesn't support iframes
                    </iframe>
                </grid-item>

                <grid-item :x=4 :y=0 :w=4 :h=12 :i=1 :key="Logs">
                    <iframe
                        src="http://127.0.0.1:9000"
                        id="logs"
                        allowfullscreen
                        frameborder="0"
                        wmode="transparent"
                    >
                        Your browser doesn't support iframes
                    </iframe>
                </grid-item> -->
                </grid-item>
            </grid-layout>
        </div>
    </div>
</template>


<script lang="ts">
import { Streamlit } from "streamlit-component-lib";
import { GridLayout, GridItem } from "vue-grid-layout";

export default {
    name: "MyComponent",
    props: ["args"], // Arguments that are passed to the plugin in Python are accessible in props `args`. Here, we access the "name" arg.
    components: {
        GridLayout,
        GridItem,
    },
    data() {
        return {
            layout: [
                { x: 0, y: 0, w: 8, h: 18, i: "0" },
                { x: 8, y: 0, w: 4, h: 9, i: "1" },
                { x: 8, y: 9, w: 4, h: 9, i: "2" },
            ],
            draggable: true,
            resizable: true,
            responsive: true,
            index: 0,
        };
    },
    computed: {
        mq() {
            const name = this.args.mq.name;
            const host = this.args.mq.host;
            const port = this.args.mq.port;
            const url = `http://${host}:${port}`;
            return { name: name, url: url };
        },
    },
    methods: {},
};
</script>


<style scoped>
input[type=checkbox] {
  display: none;
}
.label {
  border: 1px solid #000;
  display: inline-block;
  padding: 3px;
  /* background: url("unchecked.png") no-repeat left center; */ 
  /* padding-left: 15px; */
}
input[type=checkbox]:checked + .label {
  background: #f00;
  color: #fff;
  /* background-image: url("checked.png"); */
}

.vue-grid-layout {
    background: #eee;
}
.vue-grid-item:not(.vue-grid-placeholder) {
    background: #ccc;
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
    background: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='10' height='10'><circle cx='5' cy='5' r='5' fill='#999999'/></svg>")
        no-repeat;
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

#mq,
#logs {
    margin-top: 0.4rem;
    width: 100%;
    height: 100%;
    position: relative;
}
</style>