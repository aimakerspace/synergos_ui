<template>
<h1 style="background: #fff; text-align: center; boxShadow: 0 2px 3px 2px rgba(0,0,0,.1)">SYNERGOS</h1>
<el-container style="border: 1px solid #eee">

    <el-aside width="200px" style="background-color: rgb(238, 241, 246)">
        <div>
            <Formselect />
        </div>
    </el-aside>
    
    <el-container>
        <el-header style="text-align: center; font-size: 24px">
            <el-checkbox-group v-model="checkedItems" @change="checkBoxChange">
                <el-checkbox
                v-for="item in items"
                :key="item.id"
                :label="item.label"
                border
                style="margin:8px;"
                ></el-checkbox>
            </el-checkbox-group>
        </el-header>

        <el-main>
            <grid-layout
                :col-num="colNum"
                :row-height="rowHeight"
                v-model:layout="layout"
                :is-draggable="true"
                :is-resizable="true"
                :is-mirrored="false"
                :vertical-compact="true"
                :use-css-transforms="true">
                <grid-item v-for="item in layout" :key="item.i"
                    :x="item.x"
                    :y="item.y"
                    :w="item.w"
                    :h="item.h"
                    :i="item.i">

                    <div class="row-container ">
                        <div class="first-row"> 
                            <span>{{ item.label }}</span>
                        </div>
                        <iframe :src="item.url"></iframe>
                    </div>
                </grid-item>
            </grid-layout>
        </el-main>
    </el-container>    
</el-container>
</template>



<script>
import GridItem from './components/GridItem.vue';
import GridLayout from './components/GridLayout.vue';
import Formselect from './components/Formselect';
import _ from "lodash";
import { computed } from 'vue';
import { useStore } from 'vuex';


export default {

    components: {
        GridLayout,
        GridItem,
        Formselect,
    },

    setup(){
        const store = useStore()

        return {
            CNA_url: computed(() => store.getters.CNA_url),
            MLflow_url: computed(() => store.getters.MLflow_url),
            RabbitMQ_url: computed(() => store.getters.RabbitMQ_url),
            Graylog_url: computed(() => store.getters.Graylog_url),
            Amundsen_url: computed(() => store.getters.Amundsen_url),
            Neo4j_url: computed(() => store.getters.Neo4j_url)
        }
    },

    data () {
        return {
            colNum: 12,
            rowHeight: 30,
            items: [
                {
                    id: 1,
                    label: "MLflow",
                    url: `${this.MLflow_url}`     
                },
                {
                    id: 2,
                    label: "RabbitMQ",
                    url: `${this.RabbitMQ_url}`
                },
                {
                    id: 3,
                    label: "Amundsen",
                    url: `${this.Amundsen_url}`
                },
                {
                    id: 4,
                    label: "Graylog",
                    url: `${this.Graylog_url}`
                },
                {
                    id: 5,
                    label: "Neo4j",
                    url: `${this.Neo4j_url}`
                },
                {
                    id: 6,
                    label: "Dummy",
                    url: `${this.CNA_url}`
                }
            ],
            checkedItems: [],
            checkedItemsChangedBefore: [],
            layout: []
        };
    },

    methods: {
        checkBoxChange(selected) {
            if (selected.length > this.checkedItemsChangedBefore.length) {
                let label = _.difference(selected, this.checkedItemsChangedBefore)[0];
                let item = _.find(this.items, { label });
                this.addLayout(item);
            } else {
                let label = _.difference(this.checkedItemsChangedBefore, selected)[0];
                let item = _.find(this.items, { label });
                this.delLayout(item);
            }
            this.checkedItemsChangedBefore = selected;
        },
        addLayout(item) {
            this.layout.push({
                x: (this.layout.length * 6) % (this.colNum || 12),
                y: this.layout.length + (this.colNum || 12), // puts it at the bottom
                w: 6,
                h: 6,
                i: item.id,
                label: item.label,
                url: item.url,
            })
        },
        delLayout(item) {
            _.remove(this.layout, function(v) {
                return v.i === item.id;
            });
        },
    },
}
</script>



<style scoped>
.home {
    width: 100vw;
    height: 100vh;
    overflow-y: auto;
    position: relative;
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.text {
    font-size: 14px;
}

.item {
    margin-bottom: 18px;
}

.first-row {
    justify-content: space-between;
    border-style: groove; 
    text-align: center;
    align-items: center;
}
.row-container {
    display: flex; 
    width: 100%; 
    height: 100%; 
    flex-direction: column; 
    overflow: hidden;
}

.row-container iframe { 
    flex-grow: 1; 
    border: groove; 
    margin: 0; 
    padding: 0; 
    overflow:hidden
}
</style>
