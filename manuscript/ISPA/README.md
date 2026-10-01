# REALBIM Paper

*REALBIM: A Framework for Safe Early Reuse of Shared GPU Buffers Across Processes*

- [PDF](REALBIM_ISPA.pdf)
- [LaTeX source ZIP](REALBIM_ISPA_source.zip)
- [Source and build instructions](source/README.md)
- [File hashes](release.json)
- [Fresh-build verification](clean-rebuild-check.json)
- [Artifact-link verification](checks/link-update.json)

The paper has eight pages, eight figures and 25 references. Its artifact link points to the [ISPA branch](https://github.com/assasin831/readseal-artifact/tree/ISPA).

The source ZIP contains the files needed to compile the paper, editable sources for the three diagrams, and asset licenses. Older manuscripts, revision logs and one-off editing scripts are not included in the current tree.

Run `python tools/verify_manuscript.py` from the repository root to check the PDF, source ZIP and manifest. The fresh-build report checks page text, geometry, external links, fonts and rendered output. Experimental measurements are documented separately in the [data guide](../../DATA_GUIDE.md).
