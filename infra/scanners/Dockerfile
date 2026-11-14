FROM scratch
COPY scanner /scanner
COPY policy/ /policy/
COPY licenses/ /licenses/
USER 65532:65532
WORKDIR /input
ENTRYPOINT ["/scanner"]
