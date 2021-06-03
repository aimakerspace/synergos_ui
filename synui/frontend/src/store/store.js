import { createStore } from 'vuex';

export default createStore({
    state:{
        collab:'',
        project: '',
        expt: '',
        run: '',
        MLflow:'http://localhost:15000/mlflow',
        RabbitMQ:'',
        Graylog:'',
        Amundsen:'',
        Neo4j:'',
        CNA: "https://www.channelnewsasia.com/news"
    },
    mutations: {
        
    },
    getters: {
        CNA_url: state => {
        return state.CNA + '/' + state.collab + '/' + state.run
        },
        MLflow_url: state => {
            return state.MLflow
        },
        RabbitMQ_url: state => {
            return state.RabbitMQ
        },
        Graylog_url: state => {
            return state.Graylog
        },
        Amundsen_url: state => {
            return state.Amundsen
        },
        Neo4j_url: state => {
            return state.Neo4j
        }
    },
    modules: {

    }
})