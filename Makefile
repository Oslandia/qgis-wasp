MODULE_NAME=`grep '^ *name' metadata.txt | sed 's/^ *name *= *//'`
package: LICENSE README.md wasp.py metadata.txt export.svg simplify.svg configure.svg import.svg __init__.py
	rm -rf ${MODULE_NAME}
	mkdir  ${MODULE_NAME}
	cp $^  ${MODULE_NAME}
	rm -f  ${MODULE_NAME}.zip
	zip -r ${MODULE_NAME}.zip ${MODULE_NAME}
	rm -r  ${MODULE_NAME}
