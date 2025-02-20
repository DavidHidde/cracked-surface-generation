FROM debian:stable

# Install Blender
WORKDIR /usr/local
RUN apt-get update -y && apt install -y \
    wget \
    bash \
    xz-utils \
    libx11-dev \
    libxxf86vm-dev \
    libxcursor-dev \
    libxi-dev \
    libxrandr-dev \
    libxinerama-dev \
    libxkbcommon-dev \
    libwayland-dev \
    libdecor-0-dev \
    wayland-protocols \
    libdbus-1-dev \
    libgl-dev \
    libegl-dev \
    libsm-dev
RUN wget https://download.blender.org/release/Blender4.3/blender-4.3.2-linux-x64.tar.xz
RUN tar xf blender-4.3.2-linux-x64.tar.xz
RUN ln -s /usr/local/blender-4.3.2-linux-x64/blender /usr/local/bin/blender

# Install deps
WORKDIR /usr/app
COPY src/ ./
RUN blender --background --python blender_install_dependencies.py

# Run Blender as entrypoint. The .blend file and args are still expected.
ENTRYPOINT ["blender", "--background", "--python", "blender_start_render_script.py"]