<template>
  <div class="popup">
    <Vue3DraggableResizable
        :initW="450"
        :initH="350"
        v-model:x="x"
        v-model:y="y"
        v-model:w="w"
        v-model:h="h"
        v-model:active="active"
        :draggable="true">
        <div class="thumbnail">
            <iframe :src="`${CNAurl}`"></iframe> 
        </div>
      </Vue3DraggableResizable>
  </div>
</template>

<script>
import { defineComponent } from 'vue';
import Vue3DraggableResizable from 'vue3-draggable-resizable';
import 'vue3-draggable-resizable/dist/Vue3DraggableResizable.css';
import { computed } from 'vue';
import { useStore } from 'vuex';

export default defineComponent({
  components: { Vue3DraggableResizable },
    data() {
        return {
        x: 100,
        y: 100,
        h: 100,
        w: 100,
        active: false
        }
    },
    methods: {
        print(val) {
        console.log(val)
        }
    },
setup(){
    const store = useStore()

    return {
        CNAurl: computed(() => store.getters.CNAurl)
    }
}
});
</script>

<style>
.thumbnail { /* the width and height here are your resultant sizes. */
    width: 400px;
    height: 300px;
    float:left;
    margin:20px;
    position: relative;
}
 
.thumbnail iframe {
    position: relative;
    z-index: 1;
    width: 400px;   
    height: 300px;
 
    -webkit-transform-origin: 0 0;
    -moz-transform-origin: 0 0;
    transform-origin: 0 0;

 
    -webkit-transform:  scale(0.4, 0.6);   /* Gets the size down to fit into your .thumbnail. */
    -moz-transform:  scale(0.4, 0.6);      /* Gets the size down to fit into your .thumbnail. */
    transform:  scale(0.4, 0.6);           /* Gets the size down to fit into your .thumbnail. */
    overflow: hidden;
    resize: both;

}
</style>
