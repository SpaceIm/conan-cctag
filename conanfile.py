from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import functools
import os

required_conan_version = ">=1.43.0"


class CCTagConan(ConanFile):
    name = "cctag"
    description = "Detection of CCTag markers made up of concentric circles."
    license = "MPL-2.0"
    topics = ("cctag", "computer-vision", "detection", "image-processing",
              "markers", "fiducial-markers", "concentric-circles")
    homepage = "https://github.com/alicevision/CCTag"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_cuda": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_cuda": False,
    }

    exports_sources = "CMakeLists.txt"
    generators = "cmake", "cmake_find_package"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("boost/1.78.0")
        self.requires("eigen/3.4.0")
        self.requires("tbb/2020.3")
        self.requires("opencv/4.5.3")

    def validate(self):
        # FIXME: add cuda support
        if self.options.with_cuda:
            raise ConanInvalidConfiguration("CUDA not supported yet")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["CCTAG_SERIALIZE"] = False
        cmake.definitions["CCTAG_VISUAL_DEBUG"] = False
        cmake.definitions["CCTAG_NO_COUT"] = True
        cmake.definitions["CCTAG_WITH_CUDA"] = self.options.with_cuda
        cmake.definitions["CCTAG_BUILD_APPS"] = False
        cmake.definitions["CCTAG_CUDA_CC_CURRENT_ONLY"] = False
        cmake.definitions["CCTAG_NVCC_WARNINGS"] = False
        cmake.definitions["CCTAG_EIGEN_NO_ALIGN"] = True
        cmake.definitions["CCTAG_USE_POSITION_INDEPENDENT_CODE"] = self.options.get_safe("fPIC", True)
        cmake.definitions["CCTAG_ENABLE_SIMD_AVX2"] = False
        cmake.definitions["CCTAG_BUILD_TESTS"] = False
        cmake.definitions["CCTAG_BUILD_DOC"] = False
        cmake.definitions["CCTAG_NO_THRUST_COPY_IF"] = False
        cmake.configure()
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING.md", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "CCTag")
        self.cpp_info.set_property("cmake_target_name", "CCTag::CCTag")
        suffix = "d" if self.settings.buid_type == "Debug" else ""
        self.cpp_info.libs = ["CCTag{}".format(suffix)]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["dl", "pthread"])

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "CCTag"
        self.cpp_info.names["cmake_find_package_multi"] = "CCTag"