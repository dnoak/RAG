FROM docker.elastic.co/elasticsearch/elasticsearch:7.9.3

ENV discovery.type=single-node
ENV ES_JAVA_OPTS=-Xms512m -Xmx512m

EXPOSE 9200 9300

VOLUME ["/usr/share/elasticsearch/data"]
