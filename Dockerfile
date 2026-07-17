FROM ubuntu:24.04@sha256:4fbb8e6a8395de5a7550b33509421a2bafbc0aab6c06ba2cef9ebffbc7092d90

ARG DEBIAN_FRONTEND=noninteractive
ARG RESEARCH_UID=10001

# The base image is digest-pinned. Ubuntu archive package versions are not
# pinned because the public archive does not retain every superseded package;
# an image build log must therefore record the resolved package versions.
RUN apt-get update \
    && apt-get install --yes --no-install-recommends \
        build-essential \
        ca-certificates \
        cmake \
        git \
        ninja-build \
        python3 \
        python3-pip \
        python3-venv \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid "${RESEARCH_UID}" --shell /bin/bash researcher

WORKDIR /workspace
COPY --chown=researcher:researcher . /workspace

USER researcher
ENV VIRTUAL_ENV=/home/researcher/venv
ENV PATH="${VIRTUAL_ENV}/bin:${PATH}"

RUN python3 -m venv "${VIRTUAL_ENV}" \
    && python -m pip install --no-cache-dir -e ".[test]" \
    && cmake --preset release \
    && cmake --build --preset release

# Rebuild before running the complete bounded bootstrap test suite. Heavy
# searches are intentionally not part of this image's default command.
CMD ["bash", "-lc", "cmake --build --preset release && python -m pytest"]
