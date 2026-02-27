FROM solr:9.10

USER root
RUN mkdir -p /var/solr/data
RUN chown -R solr:solr /var/solr
USER solr

# cria cores somente se não existirem
RUN test -d /var/solr/data/users || precreate-core users
RUN test -d /var/solr/data/habits || precreate-core habits
