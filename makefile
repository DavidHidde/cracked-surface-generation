# Run-time variables, change at your own leisure
scene_file := scene.blend               # src/resources/scene.blend
configuration_file := configuration.yaml  # src/resources/configuration.yaml
output_dir := docker_output            # src/resources/docker_output
missing_files_dir := assets             # src/resources/assets

device := CPU
size := 1
num_retries := 1

# Docker run variables. Recommended to not change these unless you know what you're doing
image_name := blender-crack-renderer
image_version := 1.0
container_name := "${image_name}:${image_version}"

resources_dir_local := $(PWD)/src/resources
resources_dir_container := /usr/resources
resources_dir_bind :=  -v $(resources_dir_local):$(resources_dir_container)

scene_container_path := ${resources_dir_container}/${scene_file}
config_container_path := ${resources_dir_container}/${configuration_file}
output_container_path := ${resources_dir_container}/${output_dir}
assets_container_path := ${resources_dir_container}/${missing_files_dir}

# -- Targets --
build:
	docker build --tag ${container_name} .

render:
	docker run -it --rm ${resources_dir_bind} ${container_name} ${scene_container_path} -- \
		--cycles-device ${device} \
		-s ${size} \
		-c ${config_container_path} \
		-r ${num_retries} \
		-o ${output_container_path} \
		--missing_resources_dir ${assets_container_path}

bash:
	docker run -it --rm ${resources_dir_bind} --entrypoint "/bin/bash" ${container_name}
