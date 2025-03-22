FROM quay.io/jupyter/minimal-notebook:latest

RUN mkdir /home/jovyan/resources

USER root
WORKDIR /home/jovyan

# Install dependencies: Java 21 and Maven
RUN apt-get update && apt-get install -y openjdk-21-jdk maven

# Copy the pre-created Maven project and jjava-glue project
COPY ./jupyter/java /home/jovyan/java
COPY ./jupyter/install.py /home/jovyan/install.py

# Use Maven to download dependencies for JJava
WORKDIR /home/jovyan/java

# Download the JJava jar directly
RUN mvn dependency:get -Dartifact=org.dflib.jjava:jjava:1.0-M3 -Ddest=./ -Dtransitive=false
RUN mv jjava-1.0-M3.jar jjava.jar

# Pre-download Spring AI Dependencies
RUN mvn dependency:get -Dartifact=org.springframework.ai:spring-ai-openai:1.0.0-M6
RUN mvn dependency:get -Dartifact=org.springframework.ai:spring-ai-transformers:1.0.0-M6
RUN mvn dependency:get -Dartifact=org.springframework.ai:spring-ai-redis-store:1.0.0-M6
# Pre-download Jedis
RUN mvn dependency:get -Dartifact=redis.clients:jedis:5.2.0
# Download all dependencies
RUN mvn dependency:copy-dependencies -DoutputDirectory=./lib

# Create a list of dependencies for the classpath
RUN find ./lib -name "*.jar" | tr '\n' ':' > classpath.txt
# Add the jjava.jar to the classpath
RUN echo -n "/home/jovyan/java/jjava.jar:" >> classpath.txt

# Install the kernel with classpath configuration
WORKDIR /home/jovyan
RUN python install.py --prefix /opt/conda/ --classpath $(cat /home/jovyan/java/classpath.txt)

# Pre-download Transformer Models
RUN pip install transformers torch
RUN mkdir -p /home/jovyan/.cache/huggingface/hub
# Pre-download the specific model used in Spring AI Transformers
RUN python -c "from transformers import AutoModel; AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')"

# Clean up Maven artifacts but keep the jjava.jar and lib directory
RUN rm -rf /home/jovyan/java/target /home/jovyan/java/.m2 /home/jovyan/java/pom.xml \
    /home/jovyan/java/classpath.txt \
    && rm -f /home/jovyan/install.py

# Install conda packages from environment.yml
COPY ./jupyter/environment.yml /tmp/
RUN conda env update -f /tmp/environment.yml && \
    conda clean --all -f -y && \
    fix-permissions "${CONDA_DIR}" && \
    fix-permissions "/home/${NB_USER}"

WORKDIR /home/jovyan
USER $NB_UID