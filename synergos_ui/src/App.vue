<template>
	<div class="sidenav">
		<Formselect />
	</div>
	<main class="main">
		<div class="relative">
			<h1>Click button to display components</h1>
			<button @click="() => TogglePopupCNA('buttonTriggerCNA')">CNA</button>
			<button @click="() => TogglePopupML('buttonTriggerML')">Test</button>
			<button @click="() => TogglePopupTrial('buttonTriggerTrial')">Trial</button>
			<button @click="() => TogglePopupFrame('buttonTriggerFrame')">Frame</button>
			<Popup 
				v-if="popupTriggers.buttonTriggerCNA" 
				:TogglePopup="() => TogglePopupCNA('buttonTriggerCNA')">
				
			</Popup>
			
			<MLflow
				v-if="popupTriggers.buttonTriggerML" 
				:TogglePopup="() => TogglePopupML('buttonTriggerML')">
			</MLflow>

			<Trial
				v-if="popupTriggers.buttonTriggerTrial" 
				:TogglePopup="() => TogglePopupTrial('buttonTriggerTrial')">
			</Trial>

			<Frame
				v-if="popupTriggers.buttonTriggerFrame" 
				:TogglePopup="() => TogglePopupFrame('buttonTriggerFrame')">
			</Frame>
		</div>
	</main>	
</template>

<script>
import { ref } from 'vue';
import Popup from './components/Popup';
import MLflow from './components/MLflow';
import Trial from './components/Trial';
import Formselect from './components/Formselect';
import Frame from './components/Frame';

export default {
	name:'App',
	components: {
		Popup,
		MLflow,
		Trial, 
		Formselect,
		Frame
	},
	setup () {
		const popupTriggers = ref({
			buttonTriggerCNA: false,
			buttonTriggerML: false,
			buttonTriggerTrial: false,
			buttonTriggerFrame: false
		});
		const TogglePopupCNA = (trigger) => {
			popupTriggers.value[trigger] = !popupTriggers.value[trigger]
		};
		const TogglePopupML = (trigger) => {
			popupTriggers.value[trigger] = !popupTriggers.value[trigger]
		};
		const TogglePopupTrial = (trigger) => {
			popupTriggers.value[trigger] = !popupTriggers.value[trigger]
		};
		const TogglePopupFrame = (trigger) => {
			popupTriggers.value[trigger] = !popupTriggers.value[trigger]
		};
		return {
			Popup,
			popupTriggers,
			TogglePopupCNA,
			TogglePopupML,
			TogglePopupTrial,
			TogglePopupFrame,
		}
	}
}
</script>

<style lang="scss">
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
.relative {
            padding: 10px;
            position: relative;
            background-color: #fff;
            margin: 10px;
        }
/* The sidebar menu */
.sidenav {
  height: 100%; /* Full-height: remove this if you want "auto" height */
  width: 160px; /* Set the width of the sidebar */
  position: fixed; /* Fixed Sidebar (stay in place on scroll) */
  z-index: 1; /* Stay on top */
  top: 0; /* Stay at the top */
  left: 0;
  background-color: #61d2f5; /* Black */
  overflow-x: hidden; /* Disable horizontal scroll */
  padding-top: 20px;
}
/* Style page content */
.main {
  margin-left: 160px; /* Same as the width of the sidebar */
  padding: 0px 10px;
}
.green{
   background-color: #41B883;
}
.blue{
   background-color: #35495E;
}

/* On smaller screens, where height is less than 450px, change the style of the sidebar (less padding and a smaller font size) */
@media screen and (max-height: 450px) {
  .sidenav {padding-top: 15px;}
}
</style>
