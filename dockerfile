FROM openjdk:11
COPY . /app
WORKDIR /app
RUN javac Main.java
CMD ["java", "Main"]